# How‑To: Aufgaben rund um ESP32 HUB75

Dieses Dokument sammelt kurze Rezepte für typische Aufgaben mit dem Sketch in `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Der ESP32 stellt lokal eine Web‑UI, Upload‑Workflows für Bilder/GIFs sowie eine Animation‑Engine bereit und steuert das HUB75‑Panel direkt per I2S DMA – ohne externe Server.【F:esp32Hub75/main.sketch†L1-L904】

Hinweis: Die Web‑UI bietet eine Farbpalette und ein feines Canvas‑Grid; die Zeichenfläche ist intern 64×32 und wird nur optisch skaliert.【F:esp32Hub75/main.sketch†L92-L356】

## Panel neu initialisieren (Reinit)

Die Web‑UI löst `/api/reinit` aus und initialisiert das Panel neu. Anschließend wird die UI‑Canvas geleert und das Panel per `clear` zurückgesetzt, damit Pixelart wieder sauber funktioniert.【F:esp32Hub75/main.sketch†L368-L377】【F:esp32Hub75/main.sketch†L820-L825】

## Vollbild‑Frame via WebSocket senden

Der Sketch akzeptiert binäre Frames mit folgendem Format:

- Startbyte `0x46` (`'F'`).
- Danach `64×32×2` Bytes RGB565 (Little‑Endian).

Beim Empfang wird der Frame direkt in den Framebuffer kopiert und gerendert.【F:esp32Hub75/main.sketch†L62-L65】【F:esp32Hub75/main.sketch†L693-L707】

## Bild‑Upload korrekt mappen

Der Bild‑Upload nutzt denselben Mapping‑Ablauf wie GIFs: Bild wird erst auf ein Canvas gezeichnet und dann auf 64×32 gemappt. Anschließend wird das Bild als Single‑Frame‑`anim.bin` gepackt und lokal am ESP32 wie ein GIF gerendert (kein `px`‑Flood).【F:esp32Hub75/main.sketch†L535-L799】

## WebSocket‑Status prüfen

In der UI zeigt der Status‑Pill „WS: connecting…/connected“. Falls er dauerhaft auf „connecting…“ bleibt, Browser‑Konsole prüfen und sicherstellen, dass die aktuellste Sketch‑Version geladen wird (Cache leeren, neu flashen).【F:esp32Hub75/main.sketch†L242-L536】

## Einzelpixel setzen (JSON)

Einzelpixel kannst du via JSON‑Nachricht auf `/ws` senden:

```json
{"t":"px","x":10,"y":5,"c":16711680}
```

`c` ist RGB888 (`0xRRGGBB`).【F:esp32Hub75/main.sketch†L712-L726】

## Pixelart lokal speichern/laden (Browser)

Die Buttons **Save** und **Load** speichern die aktuelle Pixelart lokal im Browser (LocalStorage) und laden sie wieder, ohne Server‑Kontakt. Nach dem Laden kannst du mit „Redraw Panel“ erneut ans Panel senden.【F:esp32Hub75/main.sketch†L286-L575】

## Pixelart erneut auf Panel zeichnen

Bei Bedarf kann die aktuelle Pixelart‑Canvas erneut ans Panel gesendet werden: Der Button „Redraw Panel“ packt die Pixelart als Single‑Frame‑`anim.bin` und lässt den ESP32 sie lokal wie ein GIF rendern (keine `px`‑Flut, keine Unterbrechung durch UI‑Jobs).【F:esp32Hub75/main.sketch†L69-L799】

## Animation abspielen

1. `anim.bin` per `POST /uploadAnim` hochladen.
2. `GET /api/anim/play` starten.
3. `GET /api/anim/stop` stoppen.

Das File wird aus LittleFS gelesen und als RLE‑RGB565 gerendert.【F:esp32Hub75/main.sketch†L827-L854】【F:esp32Hub75/main.sketch†L645-L689】

## Animationen neu generieren (GIF)

Die Web‑UI erstellt `anim.bin` direkt im Browser aus GIFs (Upload aktuell auf max. 50 Frames limitiert):

- dekodiert Frames,
- skaliert/croppt auf 64×32,
- wendet Gamma/Boost an,
- speichert RLE‑Frames.

Details zur Implementierung sind im Sketch dokumentiert.【F:esp32Hub75/main.sketch†L504-L612】

## WLED‑ähnliche Effekte starten

Die UI bietet einen eigenen Bereich für Effekte (Matrix, Blink, Colorfading, Rainbow, Kaminfeuer, Twinkle, Scanner, Waves). Start/Stop und Parameter werden per WebSocket gesteuert:

```json
{"t":"fx","mode":"matrix","run":1,"speed":80,"intensity":180,"density":120,"trail":180,"duty":160,"dir":1,"cooling":120,"sparks":120,"c1":65280,"c2":16711680}
```

`run:0` stoppt den Effekt. Der Effekt‑Modus stoppt GIF‑Animationen automatisch.【F:esp32Hub75/main.sketch†L58-L1149】

## Helligkeit steuern

Die Web‑UI sendet Helligkeitswerte per WebSocket:

```json
{"t":"bright","v":128}
```

`v` ist ein Wert von 5 bis 255 und steuert `setBrightness8` am Panel.【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】

## Uhr/Stopuhr nutzen (NTP)

Die UI enthält einen Bereich **Uhr / Stopuhr (NTP)**:

1. **Modus wählen**: `Uhr`, `Stopuhr` oder `Canvas & Media` (zurück zu Pixel/GIF/FX).
2. **Uhrformat**: `HH:MM` oder `HH:MM:SS` (Clock‑Format wird per WebSocket gesetzt).
3. **Stopuhr**: Start/Stop/Reset über Buttons; Anzeige ist immer `HH:MM:SS`.
4. **Wetter (Koblenz)**: Toggle „Wetter“ aktivieren, um unten links ein 16×16‑Icon und rechts daneben die Temperatur zu sehen (Uhr bleibt oben).
5. **LED‑Kette**: Farbe per Farbwähler einstellen; die Kette läuft in einer Minute einmal um den Panel‑Rand (Start oben links → oben rechts → unten rechts → unten links). Bei exakt einer Minute erscheint ein kompletter Rahmen.【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1363-L1408】

Zeitbezug erfolgt über NTP (`pool.ntp.org`) und TZ‑Info im Sketch. Wetterdaten kommen von `WEATHER_URL` (Open‑Meteo, Standort Koblenz).【F:esp32Hub75/main.sketch†L16-L25】【F:esp32Hub75/main.sketch†L1499-L1542】【F:esp32Hub75/main.sketch†L1924-L1927】

## Implementierungscheck (Sketch-Abgleich)

Die How‑To‑Rezepte entsprechen den implementierten Endpoints, WebSocket‑Formaten und der Animation‑Pipeline im Sketch.【F:esp32Hub75/main.sketch†L62-L739】【F:esp32Hub75/main.sketch†L827-L862】

## Zukünftige Features (Roadmap)

### Pixelart‑Editor: Load/Save auf Client

- **Export**: Pixelart als JSON vom Browser herunterladen (Datei auf dem Client speichern).
- **Import**: JSON vom Client laden und als Pixelart ins Canvas + Panel übertragen.

### Animationen im Stil von WLED

- **Matrix Kino‑Film** (Digit‑Regen mit Trails): Parameter z. B. Geschwindigkeit, Dichte, Trail‑Länge, Farbpalette/Grün‑Tint.
- **Blink**: Parameter z. B. Geschwindigkeit, Duty‑Cycle, Farbpalette, zufällige Startphasen.
- **Colorfading**: Parameter z. B. Fade‑Speed, Farbpalette, Loop‑Modus.
- **Rainbow**: Parameter z. B. Geschwindigkeit, Richtung, Sättigung/Intensität.
- **Kaminfeuer**: Parameter z. B. Flammenhöhe, Glut‑Intensität, Flacker‑Stärke, Farbpalette.
- **Twinkle**: Parameter z. B. Dichte, Speed, Intensität/Farbe.
- **Scanner**: Parameter z. B. Speed, Breite/Trail, Richtung, Farbe.
- **Waves**: Parameter z. B. Speed, Richtung, Intensität.
Status: umgesetzt (UI + Effekt‑Engine im Sketch).【F:esp32Hub75/main.sketch†L58-L1684】

## Taskliste (Nächste notwendige Aufgaben)

1. **Presets speichern/laden** per LittleFS (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L777-L805】
2. **Animation‑Builder im UI** für Pixelart‑Sequenzen (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L90-L377】
3. **Umsetzungs‑Task Animationen**: Effekt‑Engine + Effekte inkl. UI‑Parametersteuerung (umgesetzt in `main.sketch`, siehe `tasks.md`, Abschnitt B0).

## Aufgaben zur Umsetzung (Roadmap‑Features)

### Pixelart‑Editor: Load/Save auf Client

1. **JSON‑Schema definieren**: 64×32 Pixel als Array (RGB888), Metadaten (Version, Breite/Höhe).
2. **Export‑Button in UI**: Pixelart aus `pix[]` in JSON serialisieren und als Datei herunterladen.
3. **Import‑Flow in UI**: JSON laden, validieren, Pixel ins Canvas schreiben und per `px` ans Panel senden.
4. **Fehlerhandling**: UI‑Meldungen für ungültige Dateien + optional Preview.

### WLED‑ähnliche Animationen

1. **Effekt‑Engine abstrahieren** (Frame‑Tick, Parameter).
2. **Matrix Kino‑Film**: Digit‑Regen mit Trails (Speed, Density, Trail‑Length, Palette).
3. **Blink**: On/Off‑Pattern (Speed, Duty‑Cycle, Palette, Random Seed).
4. **Colorfading**: Interpolation (Fade‑Speed, Palette, Loop).
5. **Rainbow**: HSV‑Sweep (Speed, Direction, Saturation/Intensity).
6. **Kaminfeuer**: Heat‑Map/Convolution (Flame Height, Glow, Flicker, Palette).
7. **UI‑Parametersteuerung**: Dropdown + Slider, Live‑Update via WebSocket JSON.
8. **Persistenz optional**: Letzten Effekt/Parameter in LittleFS speichern.

Die umfassende Aufgabenbeschreibung befindet sich in `tasks.md`.【F:esp32Hub75/tasks.md†L1-L99】
