# Waveshare Companion – Spotify-Trefferauswahl v0.5.5

Gezielter Hotfix für Spotify-Plugin `spop` 4.5.0 auf Volumio `192.168.2.241`.

## Ursache anhand der echten Volumio-Daten

Bei der Sprachsuche **„Get Lucky von Daft Punk“** erhielten Original,
Radio-Edit und Remix bislang alle exakt `0.876`. Diese *unterschiedlichen
Aufnahmen* wurden korrekt nicht zu einer Veröffentlichung zusammengeführt,
blieben aber gleichauf – daher die Abweisung `ambiguous`.

Die vom Gerät gelieferten Titel enthalten außerdem oft Feature-/Versionsangaben,
z. B. `(feat. Pharrell Williams and Nile Rodgers)`, `(Radio Edit)` oder
`(Daft Punk Remix)`. Der reine Textvergleich behandelte sie nicht getrennt.

## Neue Auswahl

- Titelgrundform und Hauptinterpret müssen übereinstimmen.
- Bei **nicht gewünschter Version** gewinnt die Standard-/Albumaufnahme.
- Bei **ausdrücklich gewünschter Version** wird ein passender Remix, Radio Edit
  oder anderer Versionszusatz bevorzugt. Der benannte Remixer muss passen.
- Identische Aufnahmen auf unterschiedlichen Releases werden zusammengefasst;
  Radio Edit und Remix bleiben *eigene* Aufnahmen.
- Bei wirklicher Mehrdeutigkeit verschiedener Songs/Interpreten erfolgt
  weiterhin keine automatische Wiedergabe.
- Falls eine angeforderte Version nicht gefunden wird, wird nicht stillschweigend
  die Standardversion abgespielt.

Mit den realen Kandidaten wird bei `Get Lucky von Daft Punk` die Standardaufnahme
vom Album **Random Access Memories** ausgewählt:
`spotify:track:69kOkLUCkxIZYexIgSG8rq`.
Bei ausdrücklicher Anfrage des Daft-Punk-Remixes wird anhand der Version
`spotify:track:78NwNb2BPO7OKDYYRWB1WT` gewählt, sofern diese unter den
Suchergebnissen ist.

## Installation

```bash
cd /srv/ai/projects
wget -qO waveshare-volumio-v0.5.5.zip https://raw.githubusercontent.com/tyvda/ScriptBase/waveshare-companion-volumio-v0.5.5/waveshare-companion/waveshare-volumio-v0.5.5.zip
# SHA-256-Prüfung mit dem im Release genannten Wert
unzip -oq waveshare-volumio-v0.5.5.zip
bash waveshare-volumio-v0.5.5/update_search.sh /srv/ai/projects/companion-mvp/server
```

Der Installer sichert die vorherige Controller-Datei und tauscht ausschließlich
`server/volumio_controller.py` aus; `app.py`, `pipeline.py`, Modelle, Audio- und
WLAN-Konfiguration bleiben unverändert. Rollback beim fehlgeschlagenen Dienststart.

## Read-only-Diagnose

```bash
/srv/ai/projects/companion-mvp/server/.venv/bin/python \
  /srv/ai/projects/waveshare-volumio-v0.5.5/diagnose_spotify.py \
  'Get Lucky von Daft Punk'
```

Erwartet: Standardaufnahme über Radio Edit und Remix, mit entsprechend höherem Score.
Keine Musik wird dabei gestartet.

## Wiedergabe (verändert die Warteschlange)

```bash
curl -sS -X POST http://127.0.0.1:8000/api/volumio/spotify/play \
  -H 'Content-Type: application/json' \
  -d '{"query":"Get Lucky von Daft Punk"}'
```

Die Antwort `accepted=true` bestätigt die Annahme durch Volumio, nicht die
tatsächliche Audiowiedergabe. Den Playerstatus separat abrufen:

```bash
curl -fsS http://127.0.0.1:8000/api/volumio/status
```

**Tests:** `python3 -m unittest discover -s tests -v` (46 isolierte Tests, darunter
sieben neue Fälle auf Basis der echten Volumio-Kandidaten; keine externen
API-Aufrufe bei Testausführung). Ein Live-Test auf dem Gerät ist anschließend
weiterhin erforderlich.