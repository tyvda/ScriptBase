# How‑To: Aufgaben rund um ESP32 HUB75

Dieses Dokument sammelt kurze Rezepte für typische Aufgaben mit dem Sketch in `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Der ESP32 stellt lokal eine Web‑UI, Upload‑Workflows für Bilder/GIFs sowie eine Animation‑Engine bereit und steuert das HUB75‑Panel direkt per I2S DMA – ohne externe Server.【F:esp32Hub75/main.sketch†L1-L904】

Hinweis: Die Web‑UI bietet eine Farbpalette und ein feines Canvas‑Grid; die Zeichenfläche ist intern 64×32 und wird nur optisch skaliert.【F:esp32Hub75/main.sketch†L92-L356】

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

## Animation abspielen

1. `anim.bin` per `POST /uploadAnim` hochladen.
2. `GET /api/anim/play` starten.
3. `GET /api/anim/stop` stoppen.

Das File wird aus LittleFS gelesen und als RLE‑RGB565 gerendert.【F:esp32Hub75/main.sketch†L827-L854】【F:esp32Hub75/main.sketch†L645-L689】

## Animationen neu generieren (GIF)

Die Web‑UI erstellt `anim.bin` direkt im Browser aus GIFs:

- dekodiert Frames,
- skaliert/croppt auf 64×32,
- wendet Gamma/Boost an,
- speichert RLE‑Frames.

Details zur Implementierung sind im Sketch dokumentiert.【F:esp32Hub75/main.sketch†L504-L612】

## Helligkeit steuern

Die Web‑UI sendet Helligkeitswerte per WebSocket:

```json
{"t":"bright","v":128}
```

`v` ist ein Wert von 5 bis 255 und steuert `setBrightness8` am Panel.【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】

## Implementierungscheck (Sketch-Abgleich)

Die How‑To‑Rezepte entsprechen den implementierten Endpoints, WebSocket‑Formaten und der Animation‑Pipeline im Sketch.【F:esp32Hub75/main.sketch†L62-L739】【F:esp32Hub75/main.sketch†L827-L862】

## Taskliste (Nächste notwendige Aufgaben)

1. **Presets speichern/laden** per LittleFS (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L777-L805】
2. **Animation‑Builder im UI** für Pixelart‑Sequenzen (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L90-L377】
