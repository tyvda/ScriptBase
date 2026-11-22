# Waveshare Companion – Volumio/Spotify Add-on v0.5

Für das vorhandene Waveshare-Companion-Backend (Basis **v0.4.1**) auf Ubuntu LTS.
Ziel: Volumio unter **`http://192.168.2.241`**, Spotify-Plugin **v4.5.0** (`spop`).

## Installation

```bash
# Auf dem Ubuntu-Host; ZIP dorthin übertragen und entpacken:
unzip waveshare-volumio-v0.5.zip
cd waveshare-volumio-v0.5
python3 -m unittest discover -s tests -v
bash install.sh /srv/ai/projects/companion-mvp/server
systemctl --user status waveshare-companion --no-pager
python3 live_probe.py
```

Installer-Verhalten: `app.py` und `pipeline.py` werden gesichert und nur gezielt
gepatcht; drei neue Module werden unter `server/` ergänzt. Die vorhandenen
WAV-, Session-, Whisper-, Ollama- und Piper-API-Endpunkte bleiben unverändert.
`VOLUMIO_URL`, `VOLUMIO_ENABLED` und `VOLUMIO_TIMEOUT` werden in
`server/.env.companion` ergänzt, sofern sie noch nicht gesetzt sind. Bei aktivem
systemd-User-Service wird dieser neu gestartet.

**Wichtig:** Falls die Variable `VOLUMIO_ENABLED=0` bereits vorhanden ist, muss
sie manuell auf `1` geändert werden, ebenso eine abweichende `VOLUMIO_URL`.

### Wie Sprachbefehle verarbeitet werden

`ESP32-WAV -> Whisper -> music_agent -> (Volumio REST / optional Ollama JSON-Klassifizierung)
-> Antworttext -> Piper -> Antwort-WAV`. Bei normalen Fragen wird der bestehende
Ollama-Dialog unverändert aufgerufen. Es werden ausschließlich fest definierte
Musikaktionen ausgeführt; das LLM darf weder URLs noch Shell-Befehle vorgeben.

Beispiele: "Pause", "Spiele weiter", "Nächster Song", "Vorheriger Titel",
"Mach leiser", "Lautstärke auf 30 Prozent", "Was läuft gerade?",
"Spiele Get Lucky von Daft Punk auf Spotify", "Suche Daft Punk auf Spotify".

## Neue Backend-API (keine Token-Authentifizierung)

| Methode | Endpunkt | Parameter | Wirkung |
| --- | --- | --- | --- |
| GET | `/api/volumio/status` | – | Status, Titel, Künstler, Lautstärke |
| GET | `/api/volumio/sources` | – | verfügbare Musikquellen, Spotify-Sichtbarkeit |
| GET | `/api/volumio/spotify/search` | `query`, `limit=8` | Spotify-Treffer aus Volumio-REST-Suche |
| POST | `/api/volumio/spotify/play` | `{"query":"Get Lucky Daft Punk"}` | Treffer suchen und ggf. abspielen |
| POST | `/api/volumio/control` | `{"action":"pause"}` | play, pause, stop, next, prev, toggle, volume, volume_up, volume_down, mute, unmute, status |
| POST | `/api/volumio/voice` | `{"text":"Nächster Song"}` | Sprachbefehl ohne Audio testen |

`volume` bei `control`: `{"action":"volume","volume":30}`.

**HTTP-Status:** `200` bei lesbaren Ergebnissen/Befehlsannahme, `422` bei
ungültigen Parametern, `502` bei Volumio-HTTP-/Netzwerkfehlern, `503` wenn
die Integration deaktiviert ist. `POST /spotify/play` gibt auch dann `200` mit
`accepted:false, reason:"no_tracks"|"ambiguous"` zurück, wenn absichtlich
**keine Wiedergabe** gestartet wurde.

## Spotify-Suche, wichtige Einschränkung

Die offizielle Volumio-REST-API bietet `/api/v1/search?query=...` und
`/api/v1/replaceAndPlay`. Ob Plugin **4.5.0** Spotify-Treffer wirklich über
diesen REST-Suchweg liefert, muss am Gerät überprüft werden. Das Add-on
verwendet nur Suchtreffer mit `service=spop` (oder `spotify`) **und** einer
`spotify:`-URI. Lokale MPD-Treffer werden nicht als Spotify ausgegeben. Nur
abspielbare Typen `song`/`track` dürfen automatisch gestartet werden.

Bei keiner Übereinstimmung oder mehrdeutiger Auswahl wird die Wiedergabe
**nicht** verändert; die API liefert bis zu fünf Kandidaten. `replaceAndPlay`
erzeugt lediglich eine Befehlsbestätigung; eine tatsächlich gestartete
Wiedergabe muss über `/api/volumio/status` geprüft werden. Plugin 4.5.0 kann
zusätzliche Pairing-/Spotify-Premium-Einrichtung erfordern.

## Vor-Ort-Tests auf Ubuntu

Read-only:

```bash
curl -s http://192.168.2.241/api/v1/getState
curl -s 'http://192.168.2.241/api/v1/search?query=Daft%20Punk'
python3 live_probe.py --query 'Daft Punk'
```

Einen echten Steuerbefehl nur bewusst auslösen:

```bash
python3 live_probe.py --allow-play
curl -sS -X POST http://127.0.0.1:8000/api/volumio/voice \
  -H 'Content-Type: application/json' -d '{"text":"Lautstärke auf 30 Prozent"}'
```

**Sicherheit:** Alle Companion-API-Endpunkte sind weiterhin ohne Token im LAN.
Port 8000 weder per Router-Portfreigabe noch über einen öffentlichen Reverse
Proxy exponieren. Volumio-Host wird ausschließlich per Umgebungsvariable
festgelegt, nicht von der LLM-Ausgabe. Teste die Wiedergabe mit moderater
Lautstärke.

## Quelle / API

- Volumio REST: https://developers.volumio.com/api/rest-api
- Spotify 4.5.0: https://community.volumio.com/t/2026-spotify-plugin/77605

Die 23 automatisierten Tests benutzen einen **simulierten Volumio-Server**.
Ein echter Live-Test auf `192.168.2.241` wurde aus dieser Umgebung nicht ausgeführt.

### Echter Audio-Ende-zu-Ende-Test (ohne Playersteuerung)

```bash
bash live_audio_smoke_test.sh /srv/ai/projects/companion-mvp/server
```

Erzeugt per Piper „Was läuft gerade?“, sendet das WAV an den bestehenden
Companion und wartet auf Whisper → Volumio-Status → Piper. Es wird **kein**
Titel übersprungen, gestartet oder gestoppt. Die ausgegebene Antwort und das
WAV werden geprüft; bei einem Volumio-Verbindungsfehler kann der Job trotzdem
`ready` erreichen und eine entsprechend gesprochene Fehlermeldung liefern.