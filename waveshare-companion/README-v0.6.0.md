# Waveshare Companion + Volumio v0.6.0

Neue Funktionen: Artist-Play (bis zu 20 verschiedene Songs) und eine Spotify-Titelauswahl mit Swipe-UI-Backend. Der bisherige WAV-/Whisper-/Ollama-/Piper-Pfad bleibt bestehen.

**Download:** `waveshare-companion-v0.6.0.zip` in diesem Verzeichnis (SHA-256: `ec38295d3c06464faecca5eaee7aff3ff81a10bc856d265b0fd77312f0a88147`).

**Installation auf Ubuntu** (bestehendes `/srv/ai/projects/companion-mvp/server` vorausgesetzt):

```bash
cd /srv/ai/projects
wget -qO waveshare-companion-v0.6.0.zip https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-volumio-v0.6.0/waveshare-companion/waveshare-companion-v0.6.0.zip
echo 'ec38295d3c06464faecca5eaee7aff3ff81a10bc856d265b0fd77312f0a88147  waveshare-companion-v0.6.0.zip' | sha256sum -c -
unzip -oq waveshare-companion-v0.6.0.zip
bash waveshare-companion-v0.6.0/install.sh /srv/ai/projects/companion-mvp/server
```

Paket enthält: `README.md`, `API_CONTRACT_V0_6.md`, `CODEX_FRONTEND_PROMPT.md`, `openapi_v0_6.yaml`, Backend-Module, Installations-/Rollback-Skript, read-only Liveprobe und Regressionstests.

**Prüfen (nur lesen, keine Musik abspielen):**

```bash
/srv/ai/projects/companion-mvp/server/.venv/bin/python /srv/ai/projects/waveshare-companion-v0.6.0/live_probe.py --artist "Daft Punk" --search "Get Lucky"
```

Das Spotify-Browse-Verhalten des realen Volumio 4.5.0 ist noch per Live-Test zu bestätigen. Öffne die API nicht im Internet (ohne Authentifizierung).
