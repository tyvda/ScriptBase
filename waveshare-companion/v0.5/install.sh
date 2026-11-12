#!/usr/bin/env bash
set -Eeuo pipefail

BASE='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.5/waveshare-companion/v0.5'
SERVER="${1:-/srv/ai/projects/companion-mvp/server}"
SERVICE='waveshare-companion'
PATCH_SHA='34e719d7fa6aefa5be16d531e8b71d343c2454ae82c7c6bce37e031eff7661dd'
MODULE_SHA='3d41904dfa7e1394b4ec8ee00756447486c21bbdc567d9fe274cb4dd33b7227a'

command -v wget >/dev/null || { echo 'wget fehlt' >&2; exit 1; }
command -v sha256sum >/dev/null || { echo 'sha256sum fehlt' >&2; exit 1; }
[[ -f "$SERVER/app.py" && -f "$SERVER/pipeline.py" && -x "$SERVER/.venv/bin/python" ]] || {
  echo "Backend oder .venv fehlt: $SERVER" >&2; exit 1;
}
if grep -q 'version="0.5.0"' "$SERVER/app.py"; then
  echo 'Companion v0.5 ist bereits installiert.'
  exit 0
fi
grep -q 'version="0.4.1"' "$SERVER/app.py" || {
  echo 'Dieses Upgrade erwartet exakt Companion v0.4.1; keine Änderung.' >&2; exit 1;
}
[[ ! -e "$SERVER/app.py.before-comfyui" ]] || {
  echo 'Vorhandenes Backup app.py.before-comfyui: bitte manuell prüfen.' >&2; exit 1;
}

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/server"
wget --https-only --timeout=20 --tries=3 -qO "$TMP/apply_multimodal_patch.py" "$BASE/apply_multimodal_patch.py"
wget --https-only --timeout=20 --tries=3 -qO "$TMP/server/multimodal.py" "$BASE/server/multimodal.py"
printf '%s  %s\n' "$PATCH_SHA" "$TMP/apply_multimodal_patch.py" "$MODULE_SHA" "$TMP/server/multimodal.py" | sha256sum -c -

"$SERVER/.venv/bin/python" -m pip install 'Pillow>=10,<13'
python3 "$TMP/apply_multimodal_patch.py" "$SERVER"
"$SERVER/.venv/bin/python" -m py_compile "$SERVER/app.py" "$SERVER/multimodal.py"

if ! systemctl --user restart "$SERVICE"; then
  echo 'Service-Neustart fehlgeschlagen. app.py wird wiederhergestellt.' >&2
  cp "$SERVER/app.py.before-comfyui" "$SERVER/app.py"
  systemctl --user restart "$SERVICE" || true
  exit 1
fi
sleep 2
if ! systemctl --user is-active --quiet "$SERVICE"; then
  echo 'Service läuft nicht. app.py wird wiederhergestellt.' >&2
  cp "$SERVER/app.py.before-comfyui" "$SERVER/app.py"
  systemctl --user restart "$SERVICE" || true
  exit 1
fi

echo 'Backend v0.5 installiert und Dienst aktiv.'
echo 'ComfyUI: COMFYUI_WORKFLOW_PATH und COMFYUI_PROMPT_NODE in .env.companion konfigurieren.'
echo 'Danach: systemctl --user restart waveshare-companion'
