# How‑To: Aufgaben rund um ESP32 HUB75

Dieses Dokument sammelt kurze Rezepte für typische Aufgaben mit dem Sketch in `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Der ESP32 stellt lokal eine Web‑UI, Upload‑Workflows für Bilder/GIFs sowie eine Animation‑Engine bereit und steuert das HUB75‑Panel direkt per I2S DMA – ohne externe Server.【F:esp32Hub75/main.sketch†L1-L904】

## Panel neu initialisieren (Reinit)

Die Web‑UI löst `/api/reinit` aus und initialisiert das Panel neu. Das kann hilfreich sein, wenn das Panel beim Booten nicht korrekt gestartet ist.【F:esp32Hub75/main.sketch†L368-L369】【F:esp32Hub75/main.sketch†L820-L825】

## Vollbild‑Frame via WebSocket senden

Der Sketch akzeptiert binäre Frames mit folgendem Format:

- Startbyte `0x46` (`'F'`).
- Danach `64×32×2` Bytes RGB565 (Little‑Endian).

Beim Empfang wird der Frame direkt in den Framebuffer kopiert und gerendert.【F:esp32Hub75/main.sketch†L62-L65】【F:esp32Hub75/main.sketch†L693-L707】

## Einzelpixel setzen (JSON)

Einzelpixel kannst du via JSON‑Nachricht auf `/ws` senden:

```json
{"t":"px","x":10,"y":5,"c":16711680}
```

`c` ist RGB888 (`0xRRGGBB`).【F:esp32Hub75/main.sketch†L712-L726】

## Pixelart JSON Import/Export (Client)

- **Export**: Button „Pixelart JSON Export“ speichert den aktuellen Canvas‑State als JSON Datei.
- **Import**: Button „Pixelart JSON Import“ lädt eine JSON Datei (64×32) und sendet sie als Full‑Frame an das Panel.

Die Umsetzung ist in der Web‑UI‑Logik enthalten (Import/Export + Full‑Frame Upload).【F:esp32Hub75/main.sketch†L129-L520】

## Animation abspielen

1. `anim.bin` per `POST /uploadAnim` hochladen.
2. `GET /api/anim/play` starten.
3. `GET /api/anim/stop` stoppen.

Das File wird aus LittleFS gelesen und als RLE‑RGB565 gerendert.【F:esp32Hub75/main.sketch†L827-L854】【F:esp32Hub75/main.sketch†L645-L689】

## WLED‑ähnliche Effekte starten/stoppen

1. Effekt auswählen (Matrix, Blink, Colorfading, Rainbow, Kaminfeuer).
2. Parameter (Speed, Density/Duty/Intensity/Brightness, Colors) setzen.
3. „Start Effekt“ klicken, „Stop Effekt“ beendet den Modus.

Die Steuerung läuft über WebSocket JSON (`t:"fx"`).【F:esp32Hub75/main.sketch†L233-L931】

## Animationen neu generieren (GIF)

Die Web‑UI erstellt `anim.bin` direkt im Browser aus GIFs:

- dekodiert Frames,
- skaliert/croppt auf 64×32,
- wendet Gamma/Boost an,
- speichert RLE‑Frames.

Details zur Implementierung sind im Sketch dokumentiert.【F:esp32Hub75/main.sketch†L504-L612】

## OTA Update öffnen

- `http://hub75.local/update` oder `http://<IP>/update` im Browser öffnen.
- Firmware hochladen (ElegantOTA).【F:esp32Hub75/main.sketch†L860-L862】

## Implementierungscheck (Sketch-Abgleich)

Die How‑To‑Rezepte entsprechen den implementierten Endpoints, WebSocket‑Formaten und der Animation‑Pipeline im Sketch.【F:esp32Hub75/main.sketch†L62-L739】【F:esp32Hub75/main.sketch†L827-L862】

## Hinweis: Preview‑Redraw

Die UI nutzt Line‑Scanning per Offscreen‑Buffer und `requestAnimationFrame`, damit das Pixel‑Preview zuverlässig zeilenweise neu gezeichnet wird.【F:esp32Hub75/main.sketch†L268-L315】

## Ausblick (geplante Features)

- Presets & Parameter‑Feintuning für Effekte.
- Performance‑Profiling/Monitoring in der UI.

Konkrete Umsetzungsschritte sind in `task.md` gesammelt (Abschnitt „Nächste Aufgaben“).
