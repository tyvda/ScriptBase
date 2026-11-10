#!/usr/bin/env bash
# Migration einer bestehenden Companion-v0.1-Installation zu Backend v0.2 ohne Token.
# Usage: bash upgrade_no_token.sh [PROJECT_DIR]
# Sicherung wird angelegt; unbekannte Serverprozesse werden nicht beendet.
set -Eeuo pipefail

project_dir="${1:-$PWD/companion-mvp}"
app_file="$project_dir/server/app.py"
url='https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-mvp-v0.2/waveshare-companion/server/app.py'
expected_sha='d89a38766fba0a205ad9b3673b3099a71b19626d53697c3121fe8367435d4f1f'

if [[ ! -f "$app_file" ]]; then
  printf 'Nicht gefunden: %s\n' "$app_file" >&2
  exit 2
fi
for program in wget sha256sum python3; do
  command -v "$program" >/dev/null 2>&1 || { printf 'Fehlt: %s\n' "$program" >&2; exit 2; }
done

tmp_file="$(mktemp)"
trap 'rm -f -- "$tmp_file"' EXIT
wget --https-only --tries=3 --timeout=30 -O "$tmp_file" "$url"
printf '%s  %s\n' "$expected_sha" "$tmp_file" | sha256sum -c -
python3 -m py_compile "$tmp_file"

if cmp -s "$tmp_file" "$app_file"; then
  printf 'Backend bereits auf v0.2 ohne Token.\n'
  exit 0
fi

backup="${app_file}.before-no-token-$(date +%Y%m%d-%H%M%S).bak"
cp -p -- "$app_file" "$backup"
install -m 0644 "$tmp_file" "$app_file"
printf 'Backend aktualisiert. Backup: %s\n' "$backup"

if command -v systemctl >/dev/null 2>&1 && \
   systemctl --user is-active --quiet waveshare-companion.service; then
  systemctl --user restart waveshare-companion.service
  systemctl --user status --no-pager waveshare-companion.service
else
  printf 'Kein aktiver systemd-User-Service erkannt.\n'
  printf 'Bitte den bisherigen Companion-Prozess kontrolliert neu starten,\n'
  printf 'damit die geaenderte Python-Datei geladen wird.\n'
fi

printf 'API erfordert ab jetzt keinen Authorization-Header mehr.\n'
printf 'WICHTIG: Port 8000 nur im vertrauenswuerdigen LAN zugaenglich machen.\n'
printf 'Alter COMPANION_TOKEN-Eintrag in .env.companion wird ignoriert und kann entfernt werden.\n'
