#!/usr/bin/env bash
# Install a per-user systemd service for the already-installed Companion.
# Usage: bash setup_companion_service.sh [PROJECT_DIR]
# Does not terminate or replace any existing process on port 8000.
set -Eeuo pipefail

project_dir="${1:-$PWD/companion-mvp}"
if [[ ! -d "$project_dir/server" ]]; then
  printf 'Projekt nicht gefunden: %s\n' "$project_dir" >&2
  exit 2
fi
server_dir="$(cd "$project_dir/server" && pwd -P)"

if [[ ! -x "$server_dir/.venv/bin/uvicorn" || ! -f "$server_dir/.env.companion" ]]; then
  printf 'Die Installation ist unvollstaendig: .venv oder .env.companion fehlt.\n' >&2
  exit 2
fi
if ! command -v systemctl >/dev/null 2>&1; then
  printf 'systemctl nicht gefunden. Ubuntu mit systemd erforderlich.\n' >&2
  exit 2
fi

unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
unit_file="$unit_dir/waveshare-companion.service"
mkdir -p "$unit_dir"
if [[ -e "$unit_file" || -L "$unit_file" ]]; then
  printf 'Service-Datei existiert bereits: %s\n' "$unit_file" >&2
  printf 'Bitte zuerst pruefen, bevor sie manuell geaendert wird.\n' >&2
  exit 2
fi

umask 077
{
  printf '[Unit]\n'
  printf 'Description=Waveshare ESP32-S3 Local AI Companion\n'
  printf 'Wants=network-online.target\n'
  printf 'After=network-online.target\n\n'
  printf '[Service]\n'
  printf 'Type=simple\n'
  printf 'WorkingDirectory=%s\n' "$server_dir"
  printf 'EnvironmentFile=%s/.env.companion\n' "$server_dir"
  printf 'ExecStart="%s/.venv/bin/uvicorn" app:app --host 0.0.0.0 --port 8000\n' "$server_dir"
  printf 'Restart=on-failure\n'
  printf 'RestartSec=5\n'
  printf 'TimeoutStopSec=15\n'
  printf 'NoNewPrivileges=yes\n'
  printf 'UMask=0077\n\n'
  printf '[Install]\n'
  printf 'WantedBy=default.target\n'
} > "$unit_file"

systemctl --user daemon-reload
systemctl --user enable waveshare-companion.service

if python3 -c 'import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(("127.0.0.1",8000)) == 0 else 1)'; then
  printf '\nService installiert, aber noch nicht gestartet: Port 8000 ist bereits belegt.\n'
  printf 'Wenn der alte Companion-Prozess laeuft, dessen PID zuerst pruefen und beenden.\n'
  printf 'Anschliessend: systemctl --user start waveshare-companion.service\n'
else
  systemctl --user start waveshare-companion.service
  printf '\nService installiert und gestartet.\n'
fi

printf '\nBefehle:\n'
printf '  systemctl --user start waveshare-companion.service\n'
printf '  systemctl --user stop waveshare-companion.service\n'
printf '  systemctl --user restart waveshare-companion.service\n'
printf '  systemctl --user status waveshare-companion.service\n'
printf '  journalctl --user -u waveshare-companion.service -f\n'
printf '\nAutostart auch ohne Login (optional): sudo loginctl enable-linger %s\n' "$USER"

