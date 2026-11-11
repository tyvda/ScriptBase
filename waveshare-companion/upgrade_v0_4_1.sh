#!/usr/bin/env bash
# Fix faster-whisper/PyAV metadata_errors in an installed Companion v0.4.
# Keep installed models, virtualenv, service configuration and firmware intact.
# Usage: bash upgrade_v0_4_1.sh /srv/ai/projects/companion-mvp
set -Eeuo pipefail

project_dir="${1:-$PWD/companion-mvp}"
server_dir="$project_dir/server"
release_base='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.4.1/waveshare-companion/server'
app_sha='a44bbecddf6d74e8dbfefa8fa4a99cf59694ea166a490f4cc0716248e3e5eb22'
pipeline_sha='bab1be3952ac98400ae5ed039e057553804b222df10faec56045c6bea59684d3'

if [[ ! -f "$server_dir/app.py" || ! -f "$server_dir/pipeline.py" || \
      ! -x "$server_dir/.venv/bin/python" ]]; then
  printf 'Companion-Installation nicht gefunden unter %s\n' "$server_dir" >&2
  exit 2
fi

"$server_dir/.venv/bin/python" -c 'import numpy, faster_whisper; print("Whisper/NumPy vorhanden:", numpy.__version__)'

tmp_dir="$(mktemp -d)"
trap 'rm -rf -- "$tmp_dir"' EXIT
for name in app.py pipeline.py; do
  wget --https-only --tries=3 --timeout=30 -O "$tmp_dir/$name" "$release_base/$name"
done
printf '%s  %s\n' "$app_sha" "$tmp_dir/app.py" | sha256sum -c -
printf '%s  %s\n' "$pipeline_sha" "$tmp_dir/pipeline.py" | sha256sum -c -
"$server_dir/.venv/bin/python" -m py_compile "$tmp_dir/app.py" "$tmp_dir/pipeline.py"

backup_dir="$(mktemp -d "$server_dir/.backup-v0.4.1.XXXXXXXX")"
cp -p -- "$server_dir/app.py" "$backup_dir/app.py"
cp -p -- "$server_dir/pipeline.py" "$backup_dir/pipeline.py"
install -m 0644 "$tmp_dir/app.py" "$server_dir/app.py"
install -m 0644 "$tmp_dir/pipeline.py" "$server_dir/pipeline.py"
printf 'Whisper-Fix installiert. Backup: %s\n' "$backup_dir"

if command -v systemctl >/dev/null 2>&1 && \
   systemctl --user cat waveshare-companion.service >/dev/null 2>&1; then
  systemctl --user restart waveshare-companion.service
  systemctl --user --no-pager status waveshare-companion.service
else
  printf 'Kein systemd-User-Service gefunden. Uvicorn kontrolliert neu starten.\n'
fi

printf 'Pruefung: curl http://127.0.0.1:8000/openapi.json\n'
printf 'Echter Test: bash %s/smoke_test.sh\n' "$server_dir"
