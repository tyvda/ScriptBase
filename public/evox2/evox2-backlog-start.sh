#!/usr/bin/env bash
# EVOX2 Backlog v0.1: download, verify, register and request read-only inspection.
set -euo pipefail
URL='https://raw.githubusercontent.com/tyvda/ScriptBase/evox2-backlog-public-2026-11-15/public/evox2/EVOX2_ARBEITSVORRAT_v0.1.md'
EXPECTED_BLOB='5faacdaa319324a8a0aee731c2621e1f27508dd1'
PROJECT="$HOME/.openclaw/workspace/evox2-dev"
DEST="$PROJECT/docs/ARBEITSVORRAT.md"
if [[ ! -d "$PROJECT/.git" ]]; then
  echo "STOP: Git-Projekt nicht gefunden: $PROJECT" >&2; exit 1
fi
if [[ -e "$DEST" || -L "$DEST" ]]; then
  echo "STOP: Datei existiert bereits, kein Überschreiben: $DEST" >&2; exit 1
fi
for cmd in wget git openclaw; do
  command -v "$cmd" >/dev/null || { echo "STOP: $cmd fehlt" >&2; exit 1; }
done
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
wget --https-only --tries=2 --timeout=20 -q -O "$tmp" "$URL"
ACTUAL_BLOB=$(git hash-object "$tmp")
if [[ "$ACTUAL_BLOB" != "$EXPECTED_BLOB" ]]; then
  echo "STOP: Git-Blob-Pruefsumme stimmt nicht: $ACTUAL_BLOB" >&2; exit 1
fi
mkdir -p "$PROJECT/docs"
(umask 077; set -C; cat "$tmp" > "$DEST")
chmod 600 "$DEST"
echo "EVOX2-Arbeitsvorrat installiert: $DEST"
(cd "$PROJECT" && git status --short)
echo "Starte nur einen LESE-Durchlauf in der bestehenden OpenClaw-Instanz."
openclaw agent --agent main --message "EVOX2-Arbeitsvorrat wurde auf dem Host unter docs/ARBEITSVORRAT.md installiert. In deiner Sandbox ist das Projekt vermutlich /workspace/evox2-dev, alternativ /mnt/evox2-dev. Lies die Datei und pruefe die 18 Aufgaben samt Prioritaeten und Freigabegrenzen. Antworte mit den naechsten drei Aufgaben und ihren Voraussetzungen (maximal 250 Woerter). NUR LESEN: keine Dateien aendern, keine Systemaktionen, keine Commits, keine Folgeaufgaben starten. Der Arbeitsvorrat ist KEINE pauschale Freigabe." 
