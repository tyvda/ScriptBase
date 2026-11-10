#!/usr/bin/env bash
# Upgrade an existing Companion installation (v0.1-v0.3) to v0.4.
# Preserve virtualenv, models, .env.companion and systemd service.
# Usage: bash upgrade_v0_4.sh /srv/ai/projects/companion-mvp
set -Eeuo pipefail

project_dir="${1:-$PWD/companion-mvp}"
server_dir="$project_dir/server"
release_base='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.4/waveshare-companion/server'
app_sha='10a143b00cca6b661cbe4ae8a4d70314aa831358a5482269c00a160d9e1646d2'
pipeline_sha='3a5e07bc8c7f068a2cf0c438526135f9c426ff598c2c5c6b71507aeda34f13fb'
smoke_sha='b74e3333980c6e0de8867cc6b2c3fbeef0e34da595dd251381045ad3b110d6c0'

if [[ ! -f "$server_dir/app.py" || ! -f "$server_dir/pipeline.py" ]]; then
  printf 'Nicht gefunden: %s (erwartet app.py und pipeline.py)\n' "$server_dir" >&2
  exit 2
fi
for program in wget sha256sum python3; do
  command -v "$program" >/dev/null 2>&1 || { printf 'Fehlt: %s\n' "$program" >&2; exit 2; }
done

temp_dir="$(mktemp -d)"
trap 'rm -rf -- "$temp_dir"' EXIT
for name in app.py pipeline.py smoke_test.sh; do
  wget --https-only --tries=3 --timeout=30 -O "$temp_dir/$name" "$release_base/$name"
done
printf '%s  %s\n' "$app_sha" "$temp_dir/app.py" | sha256sum -c -
printf '%s  %s\n' "$pipeline_sha" "$temp_dir/pipeline.py" | sha256sum -c -
printf '%s  %s\n' "$smoke_sha" "$temp_dir/smoke_test.sh" | sha256sum -c -
python3 -m py_compile "$temp_dir/app.py" "$temp_dir/pipeline.py"
bash -n "$temp_dir/smoke_test.sh"

backup_dir="$(mktemp -d "$server_dir/.backup-v0.4.XXXXXXXX")"
cp -p -- "$server_dir/app.py" "$backup_dir/app.py"
cp -p -- "$server_dir/pipeline.py" "$backup_dir/pipeline.py"
if [[ -f "$server_dir/smoke_test.sh" ]]; then
  cp -p -- "$server_dir/smoke_test.sh" "$backup_dir/smoke_test.sh"
fi
install -m 0644 "$temp_dir/app.py" "$server_dir/app.py"
install -m 0644 "$temp_dir/pipeline.py" "$server_dir/pipeline.py"
install -m 0755 "$temp_dir/smoke_test.sh" "$server_dir/smoke_test.sh"
printf 'v0.4 aktualisiert. Backup: %s\n' "$backup_dir"

if command -v systemctl >/dev/null 2>&1 && \
   systemctl --user cat waveshare-companion.service >/dev/null 2>&1; then
  systemctl --user restart waveshare-companion.service
  systemctl --user status --no-pager waveshare-companion.service
else
  printf 'Kein systemd-User-Service gefunden; alten Uvicorn-Prozess kontrolliert\n'
  printf 'neu starten. Sonst bleibt weiterhin die alte Version aktiv.\n'
fi

printf 'Protokoll: PCM-WAV 16 kHz / 16 Bit / Mono, max. 10 Sekunden.\n'
printf 'Live-Pipeline-Test: bash %s/smoke_test.sh\n' "$server_dir"
