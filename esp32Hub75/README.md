# ESP32 HUB75 64×32 Web-Panel (Arduino Sketch)

Diese Dokumentation beschreibt den Sketch in `main.sketch` für ein ESP32‑Board mit HUB75‑Matrixpanel (64×32). Der Sketch stellt eine Web‑UI bereit, akzeptiert Pixel‑Zeichnen, Bild‑Uploads und GIF‑Uploads (animiert) und spielt Animationen aus dem Flash (LittleFS) ab.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Dieses Projekt ist ein standalone LED‑Matrix‑Controller für ein HUB75‑Panel (64×32, 1/16 Scan) auf Basis eines ESP32. Es bietet eine lokal gehostete Web‑Oberfläche (ohne Cloud‑Abhängigkeit), einen Pixelart‑Editor, Bild‑Upload & Skalierung, GIF‑Import & Animation und steuert das Panel direkt per I2S DMA.【F:esp32Hub75/main.sketch†L1-L904】

Kein Cloud‑Zwang, kein WLED, kein externer Server.

## Features

- Web‑UI mit Pixel‑Editor (Brush, Clear/Fill, Reinit).【F:esp32Hub75/main.sketch†L67-L377】
- Pixelart‑JSON Import/Export im Browser (lokales Load/Save).【F:esp32Hub75/main.sketch†L131-L495】
- Bild‑Upload (PNG/JPG/WebP) mit Aspect‑Mapping (Auto/4:3/16:9) und Cover/Contain‑Scaling.【F:esp32Hub75/main.sketch†L142-L454】
- GIF‑Upload inkl. browserseitiger Dekodierung und RLE‑Kompression für schnelle Wiedergabe am ESP32.【F:esp32Hub75/main.sketch†L222-L612】
- WebSocket‑Streaming von Full‑Frames (RGB565) und Einzelpixel‑Updates (JSON).【F:esp32Hub75/main.sketch†L318-L760】
- Helligkeitssteuerung im UI (WebSocket, `setBrightness8`).【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】

## Implementierungscheck (Sketch-Abgleich)

Folgende Kernfunktionen sind im aktuellen `main.sketch` implementiert und damit im Sketch nachweisbar:

- **HUB75 Panel‑Betrieb** über `ESP32-HUB75-MatrixPanel-I2S-DMA`, inklusive GPIO‑Mapping und I2S‑DMA‑Init.【F:esp32Hub75/main.sketch†L13-L166】
- **Pixelart Editor** mit Web‑UI, Brush‑Größe, Clear/Fill und Einzelpixel‑Updates über WebSocket JSON (`t:"px"`).【F:esp32Hub75/main.sketch†L90-L377】【F:esp32Hub75/main.sketch†L712-L735】
- **Bild‑Upload (PNG/JPG/WebP)** inkl. Mapping, Skalierung und Pixel‑Updates über die robuste Pixelart‑Pipeline (WebSocket JSON).【F:esp32Hub75/main.sketch†L142-L581】【F:esp32Hub75/main.sketch†L712-L726】
- **GIF‑Import & Animation** mit Browser‑Decode (`gifuct-js`), RLE‑Encoding, Upload nach LittleFS und Player auf ESP32.【F:esp32Hub75/main.sketch†L222-L689】【F:esp32Hub75/main.sketch†L827-L855】

## Product Requirements Document (PRD)

### Ziel

Ein flexibles, lokales, browserbasiertes System zur Anzeige von Pixelart, statischen Bildern und animierten GIFs auf einer HUB75 LED‑Matrix. Die Umsetzung ist im Sketch enthalten (Web‑UI, Uploads, Animationen).【F:esp32Hub75/main.sketch†L67-L904】

### Zielplattform

| Komponente | Wert |
| --- | --- |
| MCU | ESP32 (Dual Core) |
| Display | HUB75 RGB LED Matrix |
| Auflösung | 64 × 32 |
| Scan | 1/16 |
| Verbindung | WLAN |
| UI | Webbrowser (Desktop & Mobile) |

### Kernfeatures (Must‑Have)

| Feature | Beschreibung |
| --- | --- |
| Pixelart Editor | Zeichnen einzelner Pixel + Brush | 
| Farbauswahl | RGB Color Picker |
| Bilder | PNG / JPG / WebP |
| GIFs | Browserseitiges Decoding |
| Aspect Handling | Auto / 4:3 / 16:9 |
| Skalierung | Cover (Crop) / Contain (Letterbox) |
| Animation | Play / Stop / Loop |
| mDNS | Zugriff über `hub75.local` |
| Offlinefähig | Kein Internet nötig (außer CDN GIF Lib) |

Die Feature‑Implementierungen sind im Sketch sichtbar (Web‑UI, Gamma/Boost, Upload‑Pipelines, Animation‑Player).【F:esp32Hub75/main.sketch†L67-L904】

### Nice‑to‑Have (Optional)

- Presets.
- Animationen aus Pixelart.
- Multi‑Panel Support.

## Zukünftige Features (Roadmap Kurzliste)

- WLED‑ähnliche Effekte (Matrix‑Kino‑Film, Blink, Colorfading, Rainbow, Kaminfeuer).
- Effekt‑UI mit Parametern (Speed, Palette, Intensity, Effekt‑spezifische Regler).
- Persistenz für Effekte/Parameter in LittleFS.
- Preset‑Handling (Speichern/Laden von Parameter‑Sets).
- Multi‑Panel Support (Chain > 1).

## Systemarchitektur

```
Browser
 ├─ Pixel Editor
 ├─ Image Loader
 ├─ GIF Decoder (gifuct-js)
 └─ WebSocket / HTTP
        ↓
ESP32
 ├─ AsyncWebServer
 ├─ WebSocket Server
 ├─ LittleFS
 ├─ Framebuffer (RGB565)
 └─ HUB75 DMA Driver
        ↓
LED Matrix Panel
```

Die konkreten Komponenten (AsyncWebServer, WebSocket, LittleFS, Framebuffer, HUB75‑Treiber) sind im Sketch implementiert.【F:esp32Hub75/main.sketch†L4-L904】

## Abhängigkeiten (Arduino Libraries)

- `WiFi.h`, `ESPmDNS.h`, `LittleFS.h` (ESP32 Core).【F:esp32Hub75/main.sketch†L1-L3】
- `AsyncTCP.h`, `ESPAsyncWebServer.h` (Async Webserver).【F:esp32Hub75/main.sketch†L5-L6】
- `ArduinoJson.h` (JSON im WebSocket).【F:esp32Hub75/main.sketch†L7-L7】
- `ESP32-HUB75-MatrixPanel-I2S-DMA.h` (Panel‑Treiber).【F:esp32Hub75/main.sketch†L13-L13】

## Schnellstart

1. **WLAN + mDNS konfigurieren** in der `USER CONFIG` Sektion.
2. **Pins** und Panel‑Parameter in `PANEL CONFIG` / `PIN CONFIG` prüfen.
3. Sketch flashen, dann im Browser `http://<ip>/` oder `http://hub75.local/` öffnen.

Die exakten Konfigurationsstellen sind in `main.sketch` beschrieben.【F:esp32Hub75/main.sketch†L17-L56】

## Konfiguration

### WLAN & mDNS

```cpp
static const char* WIFI_SSID = "DEIN_SSID";
static const char* WIFI_PASS = "DEIN_PASS";
static const char* MDNS_NAME = "hub75";
```
【F:esp32Hub75/main.sketch†L19-L21】

### Panel‑Parameter

```cpp
#define PANEL_RES_X 64
#define PANEL_RES_Y 32
#define PANEL_CHAIN 1
```
【F:esp32Hub75/main.sketch†L26-L28】

### Pin‑Mapping (HUB75)

Die `HubPins` Struktur kapselt das Mapping. Default‑Werte sind im Sketch hinterlegt und werden mit `basePins` genutzt.【F:esp32Hub75/main.sketch†L33-L47】

## Hardware Setup

### HUB75 Pinbelegung (Mapping im Sketch)

```
r1 = 25   g1 = 26   b1 = 27
r2 = 14   g2 = 33   b2 = 32

a = 23
b = 19
c = 5
d = 17
e = -1    // 1/16 Scan

clk = 16
lat = 4
oe  = 21
```

Das Mapping entspricht den `HubPins` Default‑Werten im Sketch.【F:esp32Hub75/main.sketch†L33-L47】

### Stromversorgung

- Panel: 5V extern.
- ESP32: USB oder 5V.
- GND gemeinsam verbinden.

## Display Engine

### Framebuffer

```cpp
static uint16_t fb[PANEL_RES_X * PANEL_RES_Y];
```

Format: RGB565, direktes Rendering auf das Panel. Unterstützt Pixel‑Updates, Full‑Frame Updates und RLE‑Animationen.【F:esp32Hub75/main.sketch†L52-L689】

### Rendering

| Modus | Methode |
| --- | --- |
| Pixel | `drawPixel(x,y,color)` |
| Vollbild | Binary WebSocket Frame |
| Animation | RLE Decoding |

Die Umsetzung ist im Sketch beschrieben (WebSocket Handler, Framebuffer Copy, RLE Player).【F:esp32Hub75/main.sketch†L645-L739】

## Web‑UI & Bedienung

- **Pixel‑Zeichnen**: Linksklick malt, Rechtsklick löscht (schwarz). Brush‑Größe ist 1×1 bis 4×4.【F:esp32Hub75/main.sketch†L90-L365】
- **Farbpalette**: Schnellwahl‑Palette setzt die aktive Zeichenfarbe.【F:esp32Hub75/main.sketch†L120-L425】
- **Canvas‑Grid**: feine Linien trennen Pixel optisch, damit jedes Pixel klar erkennbar ist.【F:esp32Hub75/main.sketch†L92-L105】
- **Canvas‑Mapping**: interne Auflösung 64×32, visuell skaliert ohne Versatz.【F:esp32Hub75/main.sketch†L243-L356】
- **Clear/Fill**: Clear leert das Panel, Fill füllt mit der aktiven Farbe.【F:esp32Hub75/main.sketch†L352-L364】
- **Reinit**: Neuinitialisiert das Panel‑GPIO‑Setup per `/api/reinit`.【F:esp32Hub75/main.sketch†L368-L369】【F:esp32Hub75/main.sketch†L822-L825】
- **Gamma/Boost**: LUT‑basiert, beeinflusst Bilder & GIF‑Frames im Browser (Preview + Upload).【F:esp32Hub75/main.sketch†L151-L314】
- **Brightness**: UI‑Regler steuert die Panel‑Helligkeit (WebSocket `bright`).【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】
- **Bild‑Mapping**: Bild‑Upload folgt derselben Canvas‑Mapping‑Pipeline wie GIFs (Image → Canvas → 64×32) und zeichnet danach via Pixel‑Updates. 【F:esp32Hub75/main.sketch†L535-L590】
- **Panel‑Redraw**: Button „Redraw Panel“ sendet die aktuelle Pixelart erneut ans Panel. 【F:esp32Hub75/main.sketch†L69-L456】
- **Pixelart‑JSON**: Export/Import von Pixelart direkt im Browser (Download/Upload).【F:esp32Hub75/main.sketch†L131-L495】

### Pixelart‑JSON (Schema & Workflow)

**Schema**

```json
{
  "version": 1,
  "width": 64,
  "height": 32,
  "pixels": [0, 16711680, {"r":0,"g":255,"b":0}]
}
```

- `version`: Schema‑Version (aktuell `1`).
- `width`/`height`: müssen `64×32` sein.
- `pixels`: Array mit `64×32` Einträgen, entweder als `0xRRGGBB`‑Integer oder als `{r,g,b}`.

**Workflow**

1. **Export JSON** klickt → Browser lädt Datei herunter.
2. **Import JSON** wählt eine Datei → Validierung → Canvas + Panel werden aktualisiert.

Fehler werden im UI angezeigt, ungültige Dateien werden abgewiesen.【F:esp32Hub75/main.sketch†L260-L495】

## Netzwerk‑API (HTTP + WebSocket)

### HTTP Endpoints

- `GET /` → Web‑UI.【F:esp32Hub75/main.sketch†L815-L818】
- `GET /api/reinit` → Panel neu initialisieren.【F:esp32Hub75/main.sketch†L820-L825】
- `POST /uploadAnim` → `anim.bin` Upload nach LittleFS.【F:esp32Hub75/main.sketch†L827-L839】
- `GET /api/anim/play` → Animation starten (aus `anim.bin`).【F:esp32Hub75/main.sketch†L841-L848】
- `GET /api/anim/stop` → Animation stoppen.【F:esp32Hub75/main.sketch†L850-L854】
- `GET /ping` → Healthcheck (`pong`).【F:esp32Hub75/main.sketch†L856-L858】

### WebSocket `/ws`

- **Binary Frame**: `0x46` + `64×32×2` Bytes RGB565 (Little‑Endian).【F:esp32Hub75/main.sketch†L62-L65】【F:esp32Hub75/main.sketch†L693-L707】
- **JSON Messages**:
  - `{"t":"px","x":X,"y":Y,"c":0xRRGGBB}` – Einzelpixel setzen.【F:esp32Hub75/main.sketch†L712-L726】
  - `{"t":"clear"}` – Display löschen.【F:esp32Hub75/main.sketch†L727-L730】
  - `{"t":"fill","c":0xRRGGBB}` – Fill‑Farbe setzen.【F:esp32Hub75/main.sketch†L731-L735】
  - `{"t":"stop"}` – Animation stoppen.【F:esp32Hub75/main.sketch†L736-L739】
  - `{"t":"bright","v":128}` – Helligkeit (5–255) setzen.【F:esp32Hub75/main.sketch†L736-L768】

## Animationen (anim.bin)

Das Format wird vom Browser beim GIF‑Upload erzeugt und im ESP32 abgespielt.

### Header (16 Byte)

| Offset | Größe | Feld | Bedeutung |
| ---: | ---: | --- | --- |
| 0 | 4 | magic | `A64x` |
| 4 | 1 | w | 64 |
| 5 | 1 | h | 32 |
| 6 | 2 | frames | Anzahl Frames (LE) |
| 8 | 1 | loop | 1 = loop |
| 9 | 7 | reserved | reserviert |

Header‑Parsing auf ESP32 und Erstellung im Browser sind im Sketch dokumentiert.【F:esp32Hub75/main.sketch†L72-L88】【F:esp32Hub75/main.sketch†L556-L575】

### Frame Records

Pro Frame:

1. `delayMs` (uint16 LE)
2. `rleLen` (uint32 LE)
3. RLE‑Payload (`count` + `color` als uint16 LE)

Der ESP32 dekodiert `rleLen` Bytes in ein RGB565‑Framebuffer‑Array und rendert es direkt auf das Panel.【F:esp32Hub75/main.sketch†L645-L689】

## Netzwerk & mDNS

- `WiFi.begin(...)` verbindet das ESP32 mit dem WLAN.
- `MDNS.begin("hub75")` aktiviert `http://hub75.local`.
- WebSocket Endpoint: `/ws`.

Konfiguration und Setup laufen über `setup_wifi()` und `setup_server()`.【F:esp32Hub75/main.sketch†L792-L863】

## Performance & Stabilität

| Bereich | Bewertung |
| --- | --- |
| Pixel Editor | Echtzeit |
| Bilder | Sofort |
| GIF Playback | Stabil |
| RAM Nutzung | Kontrolliert |
| CPU Last | Niedrig |

Die Bewertung basiert auf der Architektur (FrameBuffer + RLE + WebSocket).【F:esp32Hub75/main.sketch†L52-L904】

## Bekannte Einschränkungen

- GIF CDN benötigt Internet (`gifuct-js`), alternativ kann die Library lokal gehostet werden.【F:esp32Hub75/main.sketch†L522-L536】
- Kein HTTPS (bewusst, HTTP only).【F:esp32Hub75/main.sketch†L234-L234】
- Nur ein Panel (Chain = 1).【F:esp32Hub75/main.sketch†L26-L28】

## Erweiterungsmöglichkeiten

- Mehrere Panels (Chain > 1).
- Presets speichern.
- Animation Builder im UI.
- MQTT / REST API.
- OTA Update später wieder ergänzen.

## Zukünftige Features (Roadmap)

### Animationen im Stil von WLED

Geplant ist ein eigener Animations‑Bereich mit Parametern pro Effekt:

- **Matrix Kino‑Film** (Digit‑Regen mit Trails): Parameter z. B. Geschwindigkeit, Dichte, Trail‑Länge, Farbpalette/Grün‑Tint.
- **Blink**: Parameter z. B. Geschwindigkeit, Duty‑Cycle, Farbpalette, zufällige Startphasen.
- **Colorfading**: Parameter z. B. Fade‑Speed, Farbpalette, Loop‑Modus.
- **Rainbow**: Parameter z. B. Geschwindigkeit, Richtung, Sättigung/Intensität.
- **Kaminfeuer**: Parameter z. B. Flammenhöhe, Glut‑Intensität, Flacker‑Stärke, Farbpalette.

## Taskliste (Nächste notwendige Aufgaben)

Basierend auf den dokumentierten Einschränkungen und Optional‑Features ergeben sich folgende nächste Schritte:

1. **Presets für Pixelart/Bilder**: Speichern/Laden in LittleFS integrieren (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L777-L805】
2. **Animation‑Builder im UI**: Pixelart‑Frames erfassen und als Animation exportieren (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L90-L377】

## Aufgaben zur Umsetzung (Roadmap‑Features)

### Pixelart‑Editor: Load/Save auf Client

1. **JSON‑Schema definieren**: 64×32 Pixel als Array (RGB888), Metadaten (Version, Breite/Höhe). ✅
2. **Export‑Button in UI**: Aktuelle Pixelart aus `pix[]` in JSON serialisieren und als Datei herunterladen. ✅
3. **Import‑Flow in UI**: JSON vom Client laden, validieren (Größe/Version), Pixel ins Canvas schreiben und per `px`/`fill` ans Panel übertragen. ✅
4. **Fehlerhandling**: UI‑Meldungen bei ungültigem JSON/Format; optional Vorschau vor Senden. ✅

### WLED‑ähnliche Animationen

1. **Effekt‑Engine abstrahieren**: Basisklasse/Funktionspointer für Effekte (Frame‑Tick, Parameter). Quelle: `main.sketch` (loop/Framebuffer).
2. **Matrix Kino‑Film**: Digit‑Regen mit Trails (Speed, Density, Trail‑Length, Palette). Quelle: `README.md` Roadmap.
3. **Blink**: On/Off‑Pattern (Speed, Duty‑Cycle, Palette, Random Seed). Quelle: `README.md` Roadmap.
4. **Colorfading**: Interpolation zwischen Farben (Fade‑Speed, Palette, Loop). Quelle: `README.md` Roadmap.
5. **Rainbow**: HSV‑Sweep (Speed, Direction, Saturation/Intensity). Quelle: `README.md` Roadmap.
6. **Kaminfeuer**: Heat‑Map/Convolution (Flame Height, Glow, Flicker, Palette). Quelle: `README.md` Roadmap.
7. **UI‑Parametersteuerung**: Dropdown + Parameter‑Slider, live Update über WebSocket JSON. Quelle: `main.sketch` (WebSocket).
8. **Persistenz optional**: Letzten Effekt/Parameter in LittleFS speichern (Nice‑to‑Have). Quelle: `main.sketch` (LittleFS).

Weitere Details und die vollständige Aufgabenliste liegen in `tasks.md`.【F:esp32Hub75/tasks.md†L1-L99】

## Zusammenfassung

✔ Vollständiges lokales System
✔ Kein externer Server nötig
✔ Browser als Editor
✔ Sauberer DMA‑Betrieb

Das Projekt ist produktionsreif für Installationen, Art‑Displays, Prototyping und Embedded‑Visuals.

## Dateisystem (LittleFS)

- Animationen landen in `/anim.bin` auf LittleFS (`ANIM_PATH`).【F:esp32Hub75/main.sketch†L68-L70】【F:esp32Hub75/main.sketch†L777-L805】
- Der Upload überschreibt die Datei komplett (`/uploadAnim`).【F:esp32Hub75/main.sketch†L827-L839】

## Troubleshooting

- **Keine Verbindung zur UI**: Prüfe die serielle Ausgabe (IP) und rufe `http://<ip>/` auf.【F:esp32Hub75/main.sketch†L797-L805】【F:esp32Hub75/main.sketch†L815-L818】
- **WebSocket bleibt auf „connecting…“**: Browser‑Konsole prüfen und sicherstellen, dass die UI ohne JavaScript‑Fehler lädt (aktuelle `main.sketch`‑Version flashen, Cache leeren).【F:esp32Hub75/main.sketch†L242-L536】
- **GIF Upload scheitert**: Browser lädt `gifuct-js` über CDN; ohne Internet schlägt das Laden fehl.【F:esp32Hub75/main.sketch†L522-L536】

## Dateien

- `main.sketch` – vollständiger Arduino‑Sketch mit Web‑UI und Panel‑Steuerung.【F:esp32Hub75/main.sketch†L1-L904】
