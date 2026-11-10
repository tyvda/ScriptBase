#!/usr/bin/env bash
# Reale End-to-End-Probe: Piper -> 10s-WAV -> Whisper -> Ollama -> Piper.
# Server muss bereits laufen. Kein Token. Kein Mikrofon/ESP32 erforderlich.
# Usage: bash server/smoke_test.sh [http://127.0.0.1:8000]
set -Eeuo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
base_url="${1:-http://127.0.0.1:8000}"
config="$script_dir/.env.companion"
python="$script_dir/.venv/bin/python"

if [[ ! -f "$config" || ! -x "$python" ]]; then
  printf 'Fehlt: %s oder %s\n' "$config" "$python" >&2
  exit 2
fi
for program in ffmpeg ffprobe curl; do
  command -v "$program" >/dev/null 2>&1 || { printf 'Fehlt: %s\n' "$program" >&2; exit 2; }
done

set -a
source "$config"
set +a

temp_dir="$(mktemp -d)"
trap 'rm -rf -- "$temp_dir"' EXIT

printf '[1/5] Erzeuge deutsche Testfrage mit Piper ...\n'
"$python" -m piper -m "$PIPER_MODEL" -f "$temp_dir/question-original.wav" -- \
  'Hallo Companion. Sage bitte kurz, wer du bist.'

printf '[2/5] Konvertiere auf 16 kHz, Mono, PCM s16le, maximal 10 s ...\n'
ffmpeg -nostdin -hide_banner -loglevel error -y \
  -i "$temp_dir/question-original.wav" -t 10 -ac 1 -ar 16000 \
  -c:a pcm_s16le "$temp_dir/question.wav"

printf '[3/5] Lade WAV zum Backend hoch ...\n'
turn_id="$(curl -fsS --max-time 30 -H 'Content-Type: audio/wav' \
  --data-binary "@$temp_dir/question.wav" "$base_url/api/turns?plain=1")"
if [[ ! "$turn_id" =~ ^[[:xdigit:]-]{36}$ ]]; then
  printf 'Ungueltige Turn-ID: %s\n' "$turn_id" >&2
  exit 1
fi
printf 'Turn-ID: %s\n' "$turn_id"

printf '[4/5] Warte auf Whisper -> Ollama -> Piper ...\n'
state=''
for _ in {1..300}; do
  state="$(curl -fsS --max-time 10 "$base_url/api/turns/$turn_id/state")"
  case "$state" in
    ready) break ;;
    failed|cancelled)
      curl -fsS "$base_url/api/turns/$turn_id"
      printf '\nPipeline gescheitert: %s\n' "$state" >&2
      exit 1 ;;
  esac
  sleep 1
done
if [[ "$state" != ready ]]; then
  printf 'Timeout nach 300 Sekunden (letzter Status: %s).\n' "$state" >&2
  exit 1
fi

printf '[5/5] Lade Antwort herunter und pruefe WAV-Format ...\n'
curl -fsS --max-time 120 -o "$temp_dir/answer.wav" \
  "$base_url/api/turns/$turn_id/audio.wav"
ffprobe -v error -select_streams a:0 -show_entries \
  stream=sample_rate,channels,bits_per_sample -of default=noprint_wrappers=1 \
  "$temp_dir/answer.wav"
curl -fsS "$base_url/api/turns/$turn_id" | "$python" -c \
  'import json,sys; x=json.load(sys.stdin); print("Whisper:",x["transcript"]); print("Ollama:",x["answer"]); print("Status:",x["state"])'
printf 'End-to-End-Pipeline erfolgreich.\n'
