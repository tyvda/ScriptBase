# Waveshare Companion – Spotify-Suche v0.5.4

Hotfix für wiederkehrende Ansage „Kein eindeutiger Treffer“. Kompatibel mit der
bereits installierten Volumio-Integration v0.5.3 (Volumio `192.168.2.241`, Spotify 4.5.0).

## Ursache

Der vorherige Algorithmus vergab z. B. für mehrere Veröffentlichungen von
„Get Lucky“ (Daft Punk) dieselbe Maximalwertung. Obwohl die Titelauswahl
inhaltlich eindeutig war, wurde `spotify_play()` dadurch mit `ambiguous`
abgewiesen. Mit Titel und Interpret in der Spracheingabe werden beide
Felder nun getrennt bewertet; identische Titel/Interpreten auf mehreren Alben
zählen als **eine** Auswahl. Unverwandte Titel/Interpreten werden **nicht**
automatisch abgespielt.

## Upgrade (ohne Änderungen am Audio-Worker)

```bash
cd /srv/ai/projects
wget -qO waveshare-volumio-v0.5.4.zip https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-volumio-v0.5.4/waveshare-companion/waveshare-volumio-v0.5.4.zip
# SHA-256 verifizieren, siehe Release-Begleittext
unzip -oq waveshare-volumio-v0.5.4.zip
bash waveshare-volumio-v0.5.4/update_search.sh /srv/ai/projects/companion-mvp/server
```

Der Installer tauscht **nur `server/volumio_controller.py`** aus, erstellt ein
Backup, führt einen Selbsttest aus und startet systemd neu. Bei fehlgeschlagenem
Neustart wird die Datei zurückgespielt. `app.py`, `pipeline.py` und
`.env.companion` bleiben unverändert.

## Diagnose – reine Suche, keine Playback-Änderung

```bash
/srv/ai/projects/companion-mvp/server/.venv/bin/python \
  /srv/ai/projects/waveshare-volumio-v0.5.4/diagnose_spotify.py 'Get Lucky von Daft Punk'
```

Zur Ausführung eines beabsichtigten Play-Befehls (ersetzt die Warteschlange):

```bash
curl -sS -X POST http://127.0.0.1:8000/api/volumio/spotify/play \
  -H 'Content-Type: application/json' \
  -d '{"query":"Get Lucky von Daft Punk"}'
```

## Grenzen

Es werden nur Songs aus Volumios REST-Suche mit Spotify-Service und
`spotify:`-URI verwendet. Eine erfolgreiche HTTP-Antwort von `replaceAndPlay`
ist eine Bestätigung der Anforderung, **kein** Beleg für tatsächliche
Wiedergabe. `GET /api/volumio/status` erlaubt die anschließende Prüfung.
Wenn Volumio andere Metadaten (`artist`, `title`, `type` oder `uri`) liefert,
die die Trefferbewertung nicht eindeutig machen, zeigt die Diagnose die
Kandidaten. Ohne tatsächliche Resultate von diesem Gerät wird keine
Spotify-Plugin-spezifische Struktur unterstellt.

## Tests

`python3 -m unittest discover -s tests -v` – 39 Tests, darunter
Duplikate über verschiedene Alben, Künstlerkonflikte und Audio-Routing.