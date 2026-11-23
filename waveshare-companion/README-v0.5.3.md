# Waveshare Companion – Volumio Audio-Worker v0.5.3

Hotfix für den beobachteten Fehler:
`RuntimeError: app.py: erwarteten Audio-Worker nicht gefunden; nichts verändert`
beim v0.5.2-Installer auf Ubuntu (`192.168.2.207`) mit Volumio (`192.168.2.241`).

## Änderung

Der Installer ersetzt keinen wortgleichen Quellcodeblock mehr. Er sucht mit
`ast` in der realen `work()`-Funktion die Stelle nach
`update_if_active(turn_id, transcript=transcript, state="thinking")`,
prüft die Whisper- und Piper-Aufrufe und ergänzt **dort** eine sichere
Verzweigung:

- Volumio-Befehl → `music_agent.handle_voice(transcript)` → Piper → WAV,
  **ohne** den Ollama-Textgenerator aufzurufen.
- Normale Frage → bisherige `pipeline.generate_answer()`-Logik bleibt erhalten.

Der vorhandene `pipeline.py`-Code wird nicht umgeschrieben. Dadurch bleiben
frühere lokale Anpassungen erhalten. Die Installation ist wiederholbar,
legt ein Backup an, prüft den gestarteten systemd-Dienst und stellt bei Fehlern
die Dateien wieder her. Bei unbekannter Workervariante wird mit einer
konkreten Diagnose abgebrochen statt ein ungetestetes Routing zu aktivieren.

## Installation

Nach dem SHA-256-Check und Entpacken:

```bash
bash /srv/ai/projects/waveshare-volumio-v0.5.3/install.sh /srv/ai/projects/companion-mvp/server
```

Der Installer führt `systemctl --user restart waveshare-companion.service`
aus und prüft `http://127.0.0.1:8000/api/volumio/audio-routing`.

## Kontrolle (ohne Wiedergabeänderung)

```bash
curl -fsS http://127.0.0.1:8000/api/volumio/audio-routing
# erwartet: {"version":"0.5.3","audio_worker_hook":true,"volumio_enabled":true}

bash /srv/ai/projects/waveshare-volumio-v0.5.3/live_audio_smoke_test.sh
```

Bei funktionierender Volumio-Verbindung lautet die Antwort auf „Was läuft
gerade?“ „Gerade läuft ...“ bzw. „Volumio spielt gerade nichts ...“.
Das Testskript lehnt eine generische Ollama-Antwort ab.

## Bei erneutem Fehler

```bash
bash /srv/ai/projects/waveshare-volumio-v0.5.3/diagnose_routing.sh
journalctl --user -u waveshare-companion -n 60 --no-pager
```

Für eine strukturell unbekannte `app.py` bitte zusätzlich **nur** die lokale
`work()`-Funktion als Text senden, ohne `.env.companion` oder Zugangsdaten.

## Tests

`python3 -m unittest discover -s tests -v`: 31 Tests, darunter
AST-patching bei geänderter Codeformatierung, idempotente Installation,
Rollback bei unbekanntem Worker und bei nicht geladenem Dienst (simuliertes
systemd), und Volumio-/Spotify-API-Tests mit HTTP-Mock.

Kein echter Zugriff auf den Ubuntu-Host aus der Testumgebung möglich.
Die bestehende 10-Sekunden-WAV-Schnittstelle bleibt unverändert; das Backend
hat weiterhin keine Authentifizierung und sollte nur im vertrauenswürdigen
lokalen Netz erreichbar sein.