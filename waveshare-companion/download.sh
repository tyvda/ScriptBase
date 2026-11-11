#!/usr/bin/env bash
# Download the Waveshare Local Companion MVP release over public HTTPS.
# Usage: bash download_companion.sh [PUBLIC_HTTPS_ZIP_URL]
set -euo pipefail

archive='waveshare_local_companion_mvp_v0_4_1.zip'
sha256='a65e845fa49bfba4945f8cd1653be25ccc220eb7c3dff036a39c77fbfa29af9c'
url="${1:-${COMPANION_DOWNLOAD_URL:-https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.4.1/waveshare-companion/waveshare_local_companion_mvp_v0_4_1.zip}}"

if [[ -z "$url" ]]; then
  printf 'Fehler: Oeffentliche HTTPS-URL fehlt.\n'
  printf 'Aufruf: bash %s https://example.org/%s\n' "$0" "$archive"
  exit 2
fi

if [[ "$url" != https://* ]]; then
  printf 'Fehler: Nur HTTPS-Downloads sind erlaubt.\n' >&2
  exit 2
fi

if ! command -v wget >/dev/null 2>&1 || ! command -v sha256sum >/dev/null 2>&1; then
  printf 'Bitte wget und coreutils installieren: sudo apt-get install wget coreutils\n' >&2
  exit 2
fi

part="${archive}.part"
if [[ -e "$archive" || -e "$part" ]]; then
  printf 'Fehler: %s oder %s existiert bereits; es wird nichts ueberschrieben.\n' "$archive" "$part" >&2
  exit 2
fi

trap 'rm -f -- "$part"' EXIT
printf 'Lade herunter: %s\n' "$url"
wget --https-only --tries=3 --timeout=30 --max-redirect=5 -O "$part" "$url"

printf '%s  %s\n' "$sha256" "$part" | sha256sum --check --status || {
  printf 'FEHLER: SHA-256 stimmt nicht. Die Datei wird verworfen.\n' >&2
  exit 1
}

mv -- "$part" "$archive"
printf 'SHA-256 OK: %s\n' "$archive"
printf 'Entpacken mit: unzip %s\n' "$archive"

