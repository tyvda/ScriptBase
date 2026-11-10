#!/usr/bin/env bash
# Public Ubuntu LTS installer for the Waveshare Local AI Companion MVP.
# Downloads the release ZIP, verifies SHA-256, installs local STT/TTS and starts the API.
# Ollama must already be installed, running, and have at least one model.
set -Eeuo pipefail

release_url='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.3/waveshare-companion/waveshare_local_companion_mvp_v0_3.zip'
expected_sha='6a72cc0e3a32de75b2f17bf4563b0e9ffc656aa41526b78262fae5499065f217'
service_url='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.3/waveshare-companion/setup_service.sh'
service_sha='9aa72b7c6fc928cff48fcec49926ed6104cc09e9ef61b495442c5b0602766758'
project_dir="${COMPANION_DIR:-$PWD/companion-mvp}"

for program in wget sha256sum python3 ollama; do
  if ! command -v "$program" >/dev/null 2>&1; then
    printf 'Fehlendes Programm: %s\n' "$program" >&2
    exit 2
  fi
done

if [[ -e "$project_dir" || -L "$project_dir" ]]; then
  printf 'Abbruch: Zielverzeichnis existiert bereits: %s\n' "$project_dir" >&2
  exit 2
fi

if python3 -c 'import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(("127.0.0.1",8000)) == 0 else 1)'; then
  printf 'Abbruch: TCP-Port 8000 ist bereits belegt.\n' >&2
  exit 2
fi

model="$(ollama list | awk 'NR == 2 { print $1; exit }')"
if [[ -z "$model" ]]; then
  printf 'Ollama hat kein Modell. Bitte zuerst ein Modell mit ollama pull installieren.\n' >&2
  exit 2
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf -- "$tmp_dir"' EXIT

printf 'Downloading public Companion package...\n'
wget --https-only --tries=3 --timeout=30 --max-redirect=5 \
  -O "$tmp_dir/companion.zip" "$release_url"
printf '%s  %s\n' "$expected_sha" "$tmp_dir/companion.zip" | sha256sum -c -

python3 -m zipfile -e "$tmp_dir/companion.zip" "$tmp_dir/unpacked"
if [[ ! -f "$tmp_dir/unpacked/companion-mvp/server/setup_ubuntu.sh" ]]; then
  printf 'Unerwarteter Paketinhalt – Installation abgebrochen.\n' >&2
  exit 1
fi

mv "$tmp_dir/unpacked/companion-mvp" "$project_dir"
printf 'Installing faster-whisper, Piper and German voice model...\n'
bash "$project_dir/server/setup_ubuntu.sh"

config="$project_dir/server/.env.companion"
umask 077
{
  printf 'OLLAMA_URL=%q\n' 'http://127.0.0.1:11434'
  printf 'OLLAMA_MODEL=%q\n' "$model"
  printf 'PIPER_MODEL=%q\n' "$project_dir/server/models/de_DE-thorsten-medium.onnx"
  printf 'WHISPER_MODEL=%q\n' 'small'
  printf 'WHISPER_DEVICE=%q\n' 'cpu'
  printf 'WHISPER_COMPUTE_TYPE=%q\n' 'int8'
} > "$config"

printf 'Installing systemd user service...\n'
wget --https-only --tries=3 --timeout=30 --max-redirect=5 \
  -O "$tmp_dir/setup_service.sh" "$service_url"
printf '%s  %s\n' "$service_sha" "$tmp_dir/setup_service.sh" | sha256sum -c -
bash "$tmp_dir/setup_service.sh" "$project_dir"

healthy=0
for _ in {1..20}; do
  if "$project_dir/server/.venv/bin/python" -c \
    'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)' \
    >/dev/null 2>&1; then
    healthy=1
    break
  fi
  sleep 1
done

if [[ "$healthy" != 1 ]]; then
  printf 'Serverstart fehlgeschlagen. Log: %s\n' "$project_dir/server/server.log" >&2
  exit 1
fi

printf '\nCOMPANION STARTED: http://127.0.0.1:8000/health\n'
printf 'OLLAMA MODEL: %s\n' "$model"
printf 'ESP32 SERVER URL: http://<UBUNTU-LAN-IP>:8000\n'
printf 'Config (keep private): %s\n' "$config"
printf 'Dienstverwaltung: systemctl --user start|stop|restart waveshare-companion\n'
printf 'ACHTUNG: API ohne Authentifizierung. Port 8000 nur im vertrauenswuerdigen LAN freigeben.\n'

