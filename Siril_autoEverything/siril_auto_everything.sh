#!/usr/bin/env bash
# Siril Auto-Everything orchestration script
# Builds a linear processing chain with QC for deep-sky FITS inputs.

set -euo pipefail

SIRIL_BIN=${SIRIL_BIN:-siril}
INPUT_FITS=""
WORK_DIR=""
OUTPUT_DIR=""
LOG_DIR=""
METRICS_DIR=""
CURRENT_IMAGE=""
BACKGROUND_ORDER=4
DENOISE_METHOD="sdenoise"
DECONVOLUTION_ENABLED=true

usage() {
  cat <<'USAGE'
Usage: siril_auto_everything.sh -i INPUT_FITS -w WORK_DIR -o OUTPUT_DIR [--skip-deconvolution]

Options:
  -i, --input                Path to the stacked FITS file to process.
  -w, --work-dir             Working directory for intermediate files (will be created if missing).
  -o, --output-dir           Directory where final outputs are written (created if missing).
  --skip-deconvolution       Disable the optional deconvolution step.
  -h, --help                 Show this help text.

Environment:
  SIRIL_BIN                  Path to the Siril binary (default: siril).
USAGE
}

log(){
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*"
}

require_binary(){
  if ! command -v "$1" >/dev/null 2>&1; then
    log "ERROR: Required binary '$1' not found in PATH"
    exit 1
  fi
}

ensure_dirs(){
  mkdir -p "$WORK_DIR" "$OUTPUT_DIR"
  LOG_DIR="$WORK_DIR/logs"
  METRICS_DIR="$WORK_DIR/metrics"
  mkdir -p "$LOG_DIR" "$METRICS_DIR"
}

parse_args(){
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -i|--input)
        INPUT_FITS="$2"; shift 2;;
      -w|--work-dir)
        WORK_DIR="$2"; shift 2;;
      -o|--output-dir)
        OUTPUT_DIR="$2"; shift 2;;
      --skip-deconvolution)
        DECONVOLUTION_ENABLED=false; shift 1;;
      -h|--help)
        usage; exit 0;;
      *)
        log "Unknown argument: $1"; usage; exit 1;;
    esac
  done
}

validate_args(){
  if [[ -z "$INPUT_FITS" || -z "$WORK_DIR" || -z "$OUTPUT_DIR" ]]; then
    usage
    exit 1
  fi
  if [[ ! -f "$INPUT_FITS" ]]; then
    log "ERROR: Input FITS '$INPUT_FITS' not found"
    exit 1
  fi
}

build_script(){
  local script_file="$1"
  local body="$2"
  cat >"$script_file" <<EOF_SCRIPT
requires 1.2
log
cd "$WORK_DIR"
$body
EOF_SCRIPT
}

run_siril_step(){
  local step_name="$1"
  local body="$2"
  local script_file="$WORK_DIR/${step_name}.ssf"
  local log_file="$LOG_DIR/${step_name}.log"
  build_script "$script_file" "$body"
  log "Running Siril step: $step_name"
  if ! "$SIRIL_BIN" -s "$script_file" >"$log_file" 2>&1; then
    log "ERROR: Siril step '$step_name' failed. See $log_file"
    return 1
  fi
  echo "$log_file"
}

parse_value(){
  local key="$1"; shift
  local file="$1"; shift || true
  grep -i "$key" "$file" | head -n1 | awk '{for (i=1;i<=NF;i++){if($i ~ /[-+]?[0-9]*\.?[0-9]+/){print $i}}}' | head -n1
}

collect_stat_metrics(){
  local stage="$1"; local log_file="$2"
  local mean=$(parse_value "Mean" "$log_file")
  local median=$(parse_value "Median" "$log_file")
  local stddev=$(parse_value "Std" "$log_file")
  local min=$(parse_value "Min" "$log_file")
  local max=$(parse_value "Max" "$log_file")
  cat >"$METRICS_DIR/stat_${stage}.json" <<EOF
{
  "stage": "$stage",
  "mean": ${mean:-null},
  "median": ${median:-null},
  "stddev": ${stddev:-null},
  "min": ${min:-null},
  "max": ${max:-null}
}
EOF
}

collect_findstar_metrics(){
  local stage="$1"; local log_file="$2"
  local detected=$(grep -i -E "Detected|found" "$log_file" | grep -Eo "[0-9]+" | head -n1)
  cat >"$METRICS_DIR/findstar_${stage}.json" <<EOF
{
  "stage": "$stage",
  "stars_detected": ${detected:-0}
}
EOF
}

collect_psf_metrics(){
  local stage="$1"; local log_file="$2"
  local fwhm=$(parse_value "FWHM" "$log_file")
  local hfd=$(parse_value "HFD" "$log_file")
  cat >"$METRICS_DIR/psf_${stage}.json" <<EOF
{
  "stage": "$stage",
  "fwhm": ${fwhm:-null},
  "hfd": ${hfd:-null}
}
EOF
}

measure_quality(){
  local stage="$1"; local image="$2"
  local stat_log=$(run_siril_step "stat_${stage}" "load \"$image\"\nstat")
  collect_stat_metrics "$stage" "$stat_log"
  local findstar_log=$(run_siril_step "findstar_${stage}" "load \"$image\"\nfindstar")
  collect_findstar_metrics "$stage" "$findstar_log"
  local psf_log=$(run_siril_step "psf_${stage}" "load \"$image\"\nfindstar\npsf")
  collect_psf_metrics "$stage" "$psf_log"
}

assess_clip_fraction(){
  local stat_json="$METRICS_DIR/stat_$1.json"
  local min_value=$(grep '"min"' "$stat_json" | awk -F ':' '{print $2}' | tr -d ' ,')
  if [[ -z "$min_value" ]]; then
    echo "0"
    return
  fi
  if (( $(echo "$min_value <= 0" | bc -l) )); then
    echo "0.01"
  else
    echo "0"
  fi
}

background_correction(){
  local clip_fraction=$(assess_clip_fraction "input")
  if (( $(echo "$clip_fraction > 0.005" | bc -l) )); then
    BACKGROUND_ORDER=3
  else
    BACKGROUND_ORDER=4
  fi
  local body="load \"$CURRENT_IMAGE\"\nfindstar\nseqmask mask_seq\nbg -order $BACKGROUND_ORDER -mask mask_seq\nsave bg_corrected.fit"
  if run_siril_step "background" "$body" >/dev/null; then
    CURRENT_IMAGE="$WORK_DIR/bg_corrected.fit"
  fi
}

photometric_calibration(){
  local body="load \"$CURRENT_IMAGE\"\nphotocal\nsave photocalibrated.fit"
  if run_siril_step "photocal" "$body" >/dev/null; then
    CURRENT_IMAGE="$WORK_DIR/photocalibrated.fit"
  else
    log "Photocalibration failed; falling back to whitebalance"
    local fallback="load \"$CURRENT_IMAGE\"\nwhitebalance\nsave whitebalanced.fit"
    run_siril_step "whitebalance" "$fallback" >/dev/null
    CURRENT_IMAGE="$WORK_DIR/whitebalanced.fit"
  fi
}

denoise_linear(){
  local stat_json="$METRICS_DIR/stat_input.json"
  local rms=$(grep '"stddev"' "$stat_json" | awk -F ':' '{print $2}' | tr -d ' ,')
  local strength=1.2
  if [[ -n "$rms" ]]; then
    if (( $(echo "$rms > 0.02" | bc -l) )); then
      strength=1.6
    fi
  fi
  local body="load \"$CURRENT_IMAGE\"\n$DENOISE_METHOD $strength\nsave denoised.fit"
  run_siril_step "denoise" "$body" >/dev/null
  CURRENT_IMAGE="$WORK_DIR/denoised.fit"
}

try_deconvolution(){
  if [[ "$DECONVOLUTION_ENABLED" != true ]]; then
    log "Skipping deconvolution per flag"
    return
  fi
  local psf_json="$METRICS_DIR/psf_input.json"
  local fwhm=$(grep '"fwhm"' "$psf_json" | awk -F ':' '{print $2}' | tr -d ' ,')
  if [[ -z "$fwhm" ]]; then
    log "No PSF data available; skipping deconvolution"
    return
  fi
  local body="load \"$CURRENT_IMAGE\"\nfindstar\npsf\ndeconv -psf $fwhm\nsave deconvolved.fit"
  run_siril_step "deconvolution" "$body" >/dev/null
  CURRENT_IMAGE="$WORK_DIR/deconvolved.fit"
}

export_outputs(){
  cp "$CURRENT_IMAGE" "$OUTPUT_DIR/final_linear.fit"
  log "Exported final linear file to $OUTPUT_DIR/final_linear.fit"
  for metric in stat_input psf_input findstar_input; do
    if [[ -f "$METRICS_DIR/${metric}.json" ]]; then
      cp "$METRICS_DIR/${metric}.json" "$OUTPUT_DIR/quality_${metric}.json"
    fi
  done
}

main(){
  parse_args "$@"
  validate_args
  require_binary "$SIRIL_BIN"
  require_binary bc
  ensure_dirs
  CURRENT_IMAGE="$WORK_DIR/linear_input.fit"
  cp "$INPUT_FITS" "$CURRENT_IMAGE"
  measure_quality "input" "$CURRENT_IMAGE"
  background_correction
  measure_quality "background" "$CURRENT_IMAGE"
  photometric_calibration
  measure_quality "calibrated" "$CURRENT_IMAGE"
  denoise_linear
  try_deconvolution
  export_outputs
  log "Processing pipeline finished"
}

main "$@"
