#!/usr/bin/env bash
# In-place upgrade for an existing Companion v0.1/v0.2 installation.
# Keeps the virtualenv, .env.companion, Piper models and systemd service.
# Usage: bash upgrade_v0_3.sh /srv/ai/projects/companion-mvp
set -Eeuo pipefail

project_dir="${1:-$PWD/companion-mvp}"
server_dir="$project_dir/server"
release_base='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.3/waveshare-companion/server'
app_sha='877ccff1ed1a32e50b3e1e71f0cf623a912461ec9a272154a2126025a9acba49'
pipeline_sha='fd4425ace0d0345814d227eb6e8590f9f1365c49419c70588a150951a434b314'

if [[ ! -f "$server_dir/app.py" || ! -f "$server_dir/pipeline.py" ]]; then
  printf 'Nicht gefunden: %s (erwartet app.py und pipeline.py)\n' "$server_dir" >&2
  exit 2
fi

for program in wget sha256sum python3; do
  command -v "$program" >/dev/null 2>&1 || { printf 'Fehlt: %s\n' "$program" >&2; exit 2; }
done

temp_dir="$(mktemp -d)"
trap 'rm -rf -- "$temp_dir"' EXIT

for name in app.py pipeline.py; do
  wget --https-only --tries=3 --timeout=30 -O "$temp_dir/$name" "$release_base/$name"
done
printf '%s  %s\n' "$app_sha" "$temp_dir/app.py" | sha256sum -c -
printf '%s  %s\n' "$pipeline_sha" "$temp_dir/pipeline.py" | sha256sum -c -
python3 -m py_compile "$temp_dir/app.py" "$temp_dir/pipeline.py"

if cmp -s "$temp_dir/app.py" "$server_dir/app.py" && \
   cmp -s "$temp_dir/pipeline.py" "$server_dir/pipeline.py"; then
  printf 'Die Python-Dateien sind bereits auf v0.3.\n'
else
  backup_dir="$(mktemp -d "$server_dir/.backup-v0.3.XXXXXXXX")"
  cp -p -- "$server_dir/app.py" "$backup_dir/app.py"
  cp -p -- "$server_dir/pipeline.py" "$backup_dir/pipeline.py"
  install -m 0644 "$temp_dir/app.py" "$server_dir/app.py"
  install -m 0644 "$temp_dir/pipeline.py" "$server_dir/pipeline.py"
  printf 'Backend-Code installiert. Sicherheitskopien: %s\n' "$backup_dir"
fi

if command -v systemctl >/dev/null 2>&1 && \
   systemctl --user cat waveshare-companion.service >/dev/null 2>&1; then
  printf 'Starte den systemd-Dienst mit v0.3 neu ...\n'
  systemctl --user restart waveshare-companion.service
  systemctl --user status --no-pager waveshare-companion.service
else
  printf 'Kein systemd-User-Service gefunden. Den bisherigen Uvicorn-Prozess\n'
  printf 'kontrolliert neu starten, damit der neue Code aktiv wird.\n'
fi

printf 'Pruefe danach: curl http://127.0.0.1:8000/api/capabilities\n'
