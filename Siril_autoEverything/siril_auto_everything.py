#!/usr/bin/env python3
"""
Python orchestrator for the Siril Auto-Everything pipeline.
Replicates the Bash template with CLI parsing, Siril script generation,
quality measurements, adaptive background correction, and optional deconvolution.
"""

import argparse
import importlib
import importlib.util
import json
import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

LOGGER = logging.getLogger("siril_auto_everything")
DEFAULT_SIRIL_BIN = os.environ.get("SIRIL_BIN", "siril")
DENOISE_METHOD = "sdenoise"
DEFAULT_BLUEPRINT_PATH = Path(__file__).resolve().with_name("blueprint_default.json")


@dataclass
class PipelinePaths:
    input_fits: Path
    work_dir: Path
    output_dir: Path
    log_dir: Path
    metrics_dir: Path


@dataclass
class PipelineConfig:
    siril_bin: str
    skip_deconvolution: bool
    background_order_high: int = 4
    background_order_low: int = 3
    asinh_strength: float = 0.18
    saturation_boost: float = 0.12
    drizzle: bool = False
    feather: bool = False
    export_name_template: str = "{object}_{session}"
    ui_state_dir: Optional[Path] = None


@dataclass
class SessionConfig:
    name: str
    input_fits: Path
    work_dir: Path
    output_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Siril Auto-Everything pipeline on a stacked FITS input.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--input", required=False, help="Path to the stacked FITS file to process.")
    parser.add_argument("-w", "--work-dir", required=True, help="Working directory for intermediate files.")
    parser.add_argument("-o", "--output-dir", required=True, help="Directory for final outputs.")
    parser.add_argument("--skip-deconvolution", action="store_true", help="Disable the optional deconvolution step.")
    parser.add_argument("--siril-bin", default=DEFAULT_SIRIL_BIN, help="Path to the Siril binary.")
    parser.add_argument("--sessions", help="Optional JSON/YAML file describing multiple sessions to process.")
    parser.add_argument("--preset", help="Optional JSON/YAML preset file for pipeline parameters.")
    parser.add_argument(
        "--ui-state-dir",
        help="Directory to write UI/session summaries for lightweight frontend consumption (JSON files).",
    )
    return parser.parse_args()


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ")


def require_binary(binary: str) -> None:
    if shutil.which(binary) is None:
        raise FileNotFoundError(f"Required binary '{binary}' not found in PATH")


def load_mapping(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file '{path}' not found")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if importlib.util.find_spec("yaml") is None:
            raise RuntimeError("PyYAML is required to parse YAML preset/session files")
        yaml_mod = importlib.import_module("yaml")
        return yaml_mod.safe_load(text) or {}
    return json.loads(text)


def load_preset(path: Optional[Path]) -> Dict:
    if path is None:
        return {}
    preset = load_mapping(path)
    validated: Dict[str, float] = {}
    if "asinh_strength" in preset:
        validated["asinh_strength"] = max(0.0, float(preset["asinh_strength"]))
    if "saturation_boost" in preset:
        validated["saturation_boost"] = max(0.0, float(preset["saturation_boost"]))
    if "background_order_high" in preset:
        validated["background_order_high"] = int(preset["background_order_high"])
    if "background_order_low" in preset:
        validated["background_order_low"] = int(preset["background_order_low"])
    if "drizzle" in preset:
        validated["drizzle"] = bool(preset["drizzle"])
    if "feather" in preset:
        validated["feather"] = bool(preset["feather"])
    if "export_name_template" in preset:
        validated["export_name_template"] = str(preset["export_name_template"])
    return validated


def load_effective_preset(args: argparse.Namespace) -> Dict:
    if args.preset:
        return load_preset(Path(args.preset).expanduser())
    if DEFAULT_BLUEPRINT_PATH.exists():
        LOGGER.info("No preset provided; using blueprint default at %s", DEFAULT_BLUEPRINT_PATH)
        return load_preset(DEFAULT_BLUEPRINT_PATH)
    LOGGER.info("No preset provided; proceeding with built-in defaults")
    return {}


def build_config(args: argparse.Namespace, preset: Dict) -> PipelineConfig:
    return PipelineConfig(
        siril_bin=args.siril_bin,
        skip_deconvolution=args.skip_deconvolution,
        background_order_high=preset.get("background_order_high", 4),
        background_order_low=preset.get("background_order_low", 3),
        asinh_strength=preset.get("asinh_strength", 0.18),
        saturation_boost=preset.get("saturation_boost", 0.12),
        drizzle=bool(preset.get("drizzle", False)),
        feather=bool(preset.get("feather", False)),
        export_name_template=preset.get("export_name_template", "{object}_{session}"),
        ui_state_dir=Path(args.ui_state_dir).expanduser().resolve() if args.ui_state_dir else None,
    )


def ensure_dirs(input_fits: Path, work_dir: Path, output_dir: Path) -> PipelinePaths:
    log_dir = work_dir / "logs"
    metrics_dir = work_dir / "metrics"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return PipelinePaths(input_fits=input_fits, work_dir=work_dir, output_dir=output_dir, log_dir=log_dir, metrics_dir=metrics_dir)


def slugify(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return safe or "export"


def extract_header_metadata(path: Path) -> Dict[str, str]:
    keys: Dict[str, str] = {}
    if not path.exists():
        return keys
    if importlib.util.find_spec("astropy") is None:
        return keys
    fits_mod = importlib.import_module("astropy.io.fits")
    with fits_mod.open(path) as hdul:
        header = hdul[0].header
        for key in ("OBJECT", "EXPTIME", "FILTER", "DATE-OBS"):
            if key in header:
                keys[key.lower()] = str(header[key])
    return keys


def resolve_sessions(args: argparse.Namespace, preset: Dict) -> List[SessionConfig]:
    sessions: List[SessionConfig] = []
    if args.sessions:
        mapping = load_mapping(Path(args.sessions).expanduser())
        for entry in mapping.get("sessions", []):
            input_path = Path(entry["input"]).expanduser().resolve()
            name = entry.get("name") or input_path.stem
            work_dir = Path(args.work_dir).expanduser().resolve() / name
            output_dir = Path(args.output_dir).expanduser().resolve() / name
            sessions.append(SessionConfig(name=name, input_fits=input_path, work_dir=work_dir, output_dir=output_dir))
    else:
        sessions.append(
            SessionConfig(
                name="default",
                input_fits=Path(args.input).expanduser().resolve(),
                work_dir=Path(args.work_dir).expanduser().resolve(),
                output_dir=Path(args.output_dir).expanduser().resolve(),
            )
        )
    drizzle = preset.get("drizzle", False)
    feather = preset.get("feather", False)
    if drizzle or feather:
        LOGGER.info("Preset requests drizzle=%s, feather=%s; ensure upstream stacks respect this", drizzle, feather)
    return sessions


def build_script(script_path: Path, work_dir: Path, body: str) -> None:
    script_path.write_text(f"requires 1.2\nlog\ncd \"{work_dir}\"\n{body}\n", encoding="utf-8")


def run_siril_step(step_name: str, paths: PipelinePaths, siril_bin: str, body: str) -> Path:
    script_path = paths.work_dir / f"{step_name}.ssf"
    log_path = paths.log_dir / f"{step_name}.log"
    build_script(script_path, paths.work_dir, body)
    LOGGER.info("Running Siril step: %s", step_name)
    with log_path.open("w", encoding="utf-8") as log_handle:
        result = subprocess.run([siril_bin, "-s", str(script_path)], stdout=log_handle, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, [siril_bin, "-s", str(script_path)], None, None, str(log_path))
    return log_path


def parse_value(log_path: Path, key: str) -> Optional[float]:
    pattern = re.compile(rf"{re.escape(key)}[^\d+-]*([-+]?\d*\.\d+|\d+)", re.IGNORECASE)
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.search(line)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def collect_stat_metrics(stage: str, log_path: Path, metrics_dir: Path) -> None:
    data = {
        "stage": stage,
        "mean": parse_value(log_path, "Mean"),
        "median": parse_value(log_path, "Median"),
        "stddev": parse_value(log_path, "Std"),
        "min": parse_value(log_path, "Min"),
        "max": parse_value(log_path, "Max"),
    }
    write_json(metrics_dir / f"stat_{stage}.json", data)


def collect_findstar_metrics(stage: str, log_path: Path, metrics_dir: Path) -> None:
    count = None
    pattern = re.compile(r"(Detected|found)\s+(\d+)", re.IGNORECASE)
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.search(line)
        if match:
            count = int(match.group(2))
            break
    write_json(metrics_dir / f"findstar_{stage}.json", {"stage": stage, "stars_detected": count if count is not None else 0})


def collect_psf_metrics(stage: str, log_path: Path, metrics_dir: Path) -> None:
    data = {"stage": stage, "fwhm": parse_value(log_path, "FWHM"), "hfd": parse_value(log_path, "HFD")}
    write_json(metrics_dir / f"psf_{stage}.json", data)


def measure_quality(stage: str, image: Path, paths: PipelinePaths, config: PipelineConfig) -> None:
    stat_log = run_siril_step(f"stat_{stage}", paths, config.siril_bin, f"load \"{image}\"\nstat")
    collect_stat_metrics(stage, stat_log, paths.metrics_dir)
    findstar_log = run_siril_step(f"findstar_{stage}", paths, config.siril_bin, f"load \"{image}\"\nfindstar")
    collect_findstar_metrics(stage, findstar_log, paths.metrics_dir)
    psf_log = run_siril_step(f"psf_{stage}", paths, config.siril_bin, f"load \"{image}\"\nfindstar\npsf")
    collect_psf_metrics(stage, psf_log, paths.metrics_dir)


def load_metric_value(metrics_dir: Path, metric: str, field: str) -> Optional[float]:
    json_path = metrics_dir / f"{metric}.json"
    if not json_path.exists():
        return None
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    value = data.get(field)
    return float(value) if value is not None else None


def assess_clip_fraction(metrics_dir: Path) -> float:
    min_value = load_metric_value(metrics_dir, "stat_input", "min")
    if min_value is None:
        return 0.0
    if min_value <= 0:
        return 0.01
    return 0.0


def background_correction(current_image: Path, paths: PipelinePaths, config: PipelineConfig) -> Path:
    clip_fraction = assess_clip_fraction(paths.metrics_dir)
    order = config.background_order_low if clip_fraction > 0.005 else config.background_order_high
    body = "".join(
        [
            f"load \"{current_image}\"\n",
            "findstar\n",
            "seqmask mask_seq\n",
            f"bg -order {order} -mask mask_seq\n",
            "save bg_corrected.fit",
        ]
    )
    run_siril_step("background", paths, config.siril_bin, body)
    return paths.work_dir / "bg_corrected.fit"


def photometric_calibration(current_image: Path, paths: PipelinePaths, config: PipelineConfig) -> Path:
    photocal_body = f"load \"{current_image}\"\nphotocal\nsave photocalibrated.fit"
    try:
        run_siril_step("photocal", paths, config.siril_bin, photocal_body)
        return paths.work_dir / "photocalibrated.fit"
    except subprocess.CalledProcessError:
        LOGGER.warning("Photocalibration failed; falling back to whitebalance")
        whitebalance_body = f"load \"{current_image}\"\nwhitebalance\nsave whitebalanced.fit"
        run_siril_step("whitebalance", paths, config.siril_bin, whitebalance_body)
        return paths.work_dir / "whitebalanced.fit"


def denoise_linear(current_image: Path, paths: PipelinePaths, config: PipelineConfig) -> tuple[Path, float]:
    rms = load_metric_value(paths.metrics_dir, "stat_input", "stddev")
    strength = 1.2
    if rms is not None and rms > 0.02:
        strength = 1.6
    body = f"load \"{current_image}\"\n{DENOISE_METHOD} {strength}\nsave denoised.fit"
    run_siril_step("denoise", paths, config.siril_bin, body)
    return paths.work_dir / "denoised.fit", strength


def quality_feedback(current_image: Path, paths: PipelinePaths, config: PipelineConfig, initial_strength: float) -> Path:
    calibrated_std = load_metric_value(paths.metrics_dir, "stat_calibrated", "stddev")
    denoised_std = load_metric_value(paths.metrics_dir, "stat_denoised", "stddev")
    if calibrated_std is None or denoised_std is None:
        return current_image
    if denoised_std <= calibrated_std * 1.1:
        return current_image
    LOGGER.warning("Denoise increased RMS (%.4f -> %.4f); lowering strength", calibrated_std, denoised_std)
    retry_strength = max(0.7, initial_strength * 0.75)
    body = f"load \"{current_image}\"\n{DENOISE_METHOD} {retry_strength}\nsave denoised.fit"
    run_siril_step("denoise_feedback", paths, config.siril_bin, body)
    refined = paths.work_dir / "denoised.fit"
    measure_quality("denoised", refined, paths, config)
    return refined


def try_deconvolution(current_image: Path, paths: PipelinePaths, config: PipelineConfig) -> Path:
    if config.skip_deconvolution:
        LOGGER.info("Skipping deconvolution per flag")
        return current_image
    fwhm = load_metric_value(paths.metrics_dir, "psf_input", "fwhm")
    if fwhm is None:
        LOGGER.info("No PSF data available; skipping deconvolution")
        return current_image
    body = f"load \"{current_image}\"\nfindstar\npsf\ndeconv -psf {fwhm}\nsave deconvolved.fit"
    run_siril_step("deconvolution", paths, config.siril_bin, body)
    return paths.work_dir / "deconvolved.fit"


def derive_blackpoint(metrics_dir: Path) -> float:
    median = (
        load_metric_value(metrics_dir, "stat_denoised", "median")
        or load_metric_value(metrics_dir, "stat_calibrated", "median")
        or 0.02
    )
    stddev = (
        load_metric_value(metrics_dir, "stat_denoised", "stddev")
        or load_metric_value(metrics_dir, "stat_calibrated", "stddev")
        or 0.01
    )
    blackpoint = max(0.0, median - 2.5 * stddev)
    return min(blackpoint, 0.25)


def stretch_and_color(current_image: Path, paths: PipelinePaths, config: PipelineConfig) -> Path:
    blackpoint = derive_blackpoint(paths.metrics_dir)
    midtone = min(0.65, blackpoint + 0.25)
    asinh_strength = config.asinh_strength
    saturation = 0.0
    rms = load_metric_value(paths.metrics_dir, "stat_denoised", "stddev") or load_metric_value(
        paths.metrics_dir, "stat_calibrated", "stddev"
    )
    if rms is not None and rms < 0.05:
        saturation = config.saturation_boost
    scnr = "scnr green 0.6\n" if rms is not None and rms > 0.025 else ""
    body = "".join(
        [
            f"load \"{current_image}\"\n",
            "autostretch\n",
            f"asinh {asinh_strength} {blackpoint}\n",
            f"mtf {blackpoint} {midtone} 1.0\n",
            scnr,
            f"saturation {saturation}\n" if saturation > 0 else "",
            "save stretched.fit\n",
            "save stretched.tif\n",
            "save stretched.png\n",
        ]
    )
    run_siril_step("stretch", paths, config.siril_bin, body)
    return paths.work_dir / "stretched.fit"


def summarize_metrics(paths: PipelinePaths) -> Path:
    summary = {
        "rms": {
            "input": load_metric_value(paths.metrics_dir, "stat_input", "stddev"),
            "background": load_metric_value(paths.metrics_dir, "stat_background", "stddev"),
            "calibrated": load_metric_value(paths.metrics_dir, "stat_calibrated", "stddev"),
            "denoised": load_metric_value(paths.metrics_dir, "stat_denoised", "stddev"),
        },
        "clip_fraction": assess_clip_fraction(paths.metrics_dir),
        "psf": {
            "fwhm": load_metric_value(paths.metrics_dir, "psf_input", "fwhm"),
            "hfd": load_metric_value(paths.metrics_dir, "psf_input", "hfd"),
        },
        "stars_detected": load_metric_value(paths.metrics_dir, "findstar_input", "stars_detected"),
    }
    summary_path = paths.output_dir / "quality_summary.json"
    write_json(summary_path, summary)
    return summary_path


def render_export_name(template: str, session_name: str, header: Dict[str, str]) -> str:
    tokens = {
        "session": slugify(session_name),
        "object": slugify(header.get("object", session_name)),
        "exptime": slugify(header.get("exptime", "")),
        "filter": slugify(header.get("filter", "")),
        "date": slugify(header.get("date-obs", "")),
    }
    try:
        base = template.format(**tokens)
    except KeyError:
        base = f"{tokens['object']}_{tokens['session']}"
    return slugify(base)


def export_outputs(linear_image: Path, stretched_image: Path, paths: PipelinePaths, config: PipelineConfig, session_name: str) -> Dict[str, Path]:
    header = extract_header_metadata(paths.input_fits)
    export_base = render_export_name(config.export_name_template, session_name, header)
    linear_destination = paths.output_dir / f"{export_base}_linear.fit"
    shutil.copy2(linear_image, linear_destination)
    LOGGER.info("Exported final linear file to %s", linear_destination)
    stretched_destination = paths.output_dir / f"{export_base}_stretched.fit"
    shutil.copy2(stretched_image, stretched_destination)
    for extra in ("stretched.tif", "stretched.png"):
        extra_path = paths.work_dir / extra
        if extra_path.exists():
            shutil.copy2(extra_path, paths.output_dir / f"{export_base}_{extra}")
    LOGGER.info("Exported stretched derivatives to %s", paths.output_dir)
    for metric in ("stat_input", "psf_input", "findstar_input", "stat_background", "stat_calibrated", "stat_denoised"):
        metric_path = paths.metrics_dir / f"{metric}.json"
        if metric_path.exists():
            shutil.copy2(metric_path, paths.output_dir / f"quality_{metric}.json")
    summary = summarize_metrics(paths)
    return {
        "linear": linear_destination,
        "stretched": stretched_destination,
        "quality": summary,
        "export_base": paths.output_dir / export_base,
        "header": header,
    }


def write_session_manifest(results: List[tuple[SessionConfig, Dict[str, Path]]], output_root: Path) -> None:
    manifest = []
    for session, artifacts in results:
        manifest.append({"session": session.name, **{key: str(val) for key, val in artifacts.items() if key != "header"}})
    write_json(output_root / "session_manifest.json", {"sessions": manifest})


def write_ui_state(session: SessionConfig, paths: PipelinePaths, artifacts: Dict[str, Path], config: PipelineConfig) -> None:
    if config.ui_state_dir is None:
        return
    config.ui_state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "session": session.name,
        "input": str(session.input_fits),
        "work_dir": str(session.work_dir),
        "output_dir": str(session.output_dir),
        "exports": {"linear": str(artifacts["linear"]), "stretched": str(artifacts["stretched"]), "quality": str(artifacts["quality"]), "base": str(artifacts["export_base"]),},
        "metrics": str(paths.metrics_dir),
        "header": artifacts.get("header", {}),
        "preset_template": config.export_name_template,
    }
    state_path = config.ui_state_dir / f"{slugify(session.name)}_ui_state.json"
    write_json(state_path, state)


def main() -> None:
    args = parse_args()
    configure_logging()
    if not args.input and not args.sessions:
        raise ValueError("Provide either --input for a single run or --sessions for multi-session processing")
    preset = load_effective_preset(args)
    config = build_config(args, preset)
    sessions = resolve_sessions(args, preset)
    require_binary(args.siril_bin)
    results: List[tuple[SessionConfig, Dict[str, Path]]] = []
    for session in sessions:
        if not session.input_fits.is_file():
            raise FileNotFoundError(f"Input FITS '{session.input_fits}' not found for session {session.name}")
        paths = ensure_dirs(session.input_fits, session.work_dir, session.output_dir)
        current_image = paths.work_dir / "linear_input.fit"
        shutil.copy2(session.input_fits, current_image)
        measure_quality("input", current_image, paths, config)
        current_image = background_correction(current_image, paths, config)
        measure_quality("background", current_image, paths, config)
        current_image = photometric_calibration(current_image, paths, config)
        measure_quality("calibrated", current_image, paths, config)
        denoised_image, strength = denoise_linear(current_image, paths, config)
        measure_quality("denoised", denoised_image, paths, config)
        current_image = quality_feedback(denoised_image, paths, config, strength)
        current_image = try_deconvolution(current_image, paths, config)
        stretched_image = stretch_and_color(current_image, paths, config)
        artifacts = export_outputs(current_image, stretched_image, paths, config, session.name)
        write_ui_state(session, paths, artifacts, config)
        results.append((session, artifacts))
        LOGGER.info("Session '%s' finished", session.name)

    if len(results) > 1:
        write_session_manifest(results, Path(args.output_dir).expanduser().resolve())
    LOGGER.info("Processing pipeline finished")


if __name__ == "__main__":
    main()
