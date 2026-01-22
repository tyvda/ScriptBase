# ESP32 HUB75 64×32 Web-Panel (Arduino Sketch)

Diese Dokumentation beschreibt den Sketch in `main.sketch` für ein ESP32‑Board mit HUB75‑Matrixpanel (64×32). Der Sketch stellt eine Web‑UI bereit, akzeptiert Pixel‑Zeichnen, Bild‑Uploads und GIF‑Uploads (animiert) und spielt Animationen aus dem Flash (LittleFS) ab.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Dieses Projekt ist ein standalone LED‑Matrix‑Controller für ein HUB75‑Panel (64×32, 1/16 Scan) auf Basis eines ESP32. Es bietet eine lokal gehostete Web‑Oberfläche (ohne Cloud‑Abhängigkeit), einen Pixelart‑Editor, Bild‑Upload & Skalierung, GIF‑Import & Animation und steuert das Panel direkt per I2S DMA.【F:esp32Hub75/main.sketch†L1-L904】

Kein Cloud‑Zwang, kein WLED, kein externer Server.

## Features

- Web‑UI mit Pixel‑Editor (Brush, Clear/Fill, Reinit).【F:esp32Hub75/main.sketch†L67-L377】
- Symbolbasierte Tab‑Navigation für Uhr, Pixelart, Anzeige, Animation und Settings (jeweils eigenes Menü).【F:esp32Hub75/main.sketch†L167-L610】
- Bild‑Upload (PNG/JPG/WebP) mit Aspect‑Mapping (Auto/4:3/16:9) und Cover/Contain‑Scaling.【F:esp32Hub75/main.sketch†L142-L454】
- GIF‑Upload inkl. browserseitiger Dekodierung und RLE‑Kompression für schnelle Wiedergabe am ESP32 (Upload aktuell auf max. 50 Frames limitiert).【F:esp32Hub75/main.sketch†L222-L612】
- WebSocket‑Streaming von Full‑Frames (RGB565) und Einzelpixel‑Updates (JSON).【F:esp32Hub75/main.sketch†L318-L760】
- Helligkeitssteuerung im UI (WebSocket, `setBrightness8`).【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】
- NTP‑Uhr (HH:MM oder HH:MM:SS) und Stopuhr (HH:MM:SS) mit einstellbarer LED‑Kettenfarbe für den Panel‑Rand.【F:esp32Hub75/main.sketch†L1279-L1340】
- Optionales Wetter‑Overlay für Koblenz im Uhr‑Modus (Temperatur + Kurzcode).【F:esp32Hub75/main.sketch†L1302-L1352】【F:esp32Hub75/main.sketch†L1455-L1484】
- WLED‑ähnliche Animationen (Matrix, Blink, Colorfading, Rainbow, Kaminfeuer, Twinkle, Scanner, Waves) mit UI‑Parametern und WebSocket‑Steuerung.【F:esp32Hub75/main.sketch†L58-L1684】

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
static const char* NTP_SERVER = "pool.ntp.org";
static const char* TZ_INFO = "UTC0";
static const char* WEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude=50.3569&longitude=7.5888&current_weather=true";
```
【F:esp32Hub75/main.sketch†L19-L25】

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

- **Designsprache**: Helles, hochwertiges UI im Teenage‑Engineering‑Stil mit Kartenlayout, Mono‑Typografie, prägnanten Status‑Pills und klarer Hierarchie zwischen Canvas und Controls.【F:esp32Hub75/main.sketch†L167-L412】
- **Tabs (Symbole)**: Oben wählst du zwischen Uhr, Pixelart, Anzeige, Animation und Settings; pro Tab erscheint das passende Menü.【F:esp32Hub75/main.sketch†L360-L694】
- **Pixel‑Zeichnen**: Linksklick malt, Rechtsklick löscht (schwarz). Brush‑Größe ist 1×1 bis 4×4.【F:esp32Hub75/main.sketch†L90-L365】
- **Farbpalette**: Schnellwahl‑Palette setzt die aktive Zeichenfarbe.【F:esp32Hub75/main.sketch†L120-L425】
- **Canvas‑Grid**: feine Linien trennen Pixel optisch, damit jedes Pixel klar erkennbar ist.【F:esp32Hub75/main.sketch†L92-L105】
- **Canvas‑Mapping**: interne Auflösung 64×32, visuell skaliert ohne Versatz.【F:esp32Hub75/main.sketch†L243-L356】
- **Clear/Fill**: Clear leert das Panel, Fill füllt mit der aktiven Farbe.【F:esp32Hub75/main.sketch†L352-L364】
- **Reinit**: Neuinitialisiert das Panel‑GPIO‑Setup per `/api/reinit`.【F:esp32Hub75/main.sketch†L368-L369】【F:esp32Hub75/main.sketch†L822-L825】
- **Gamma/Boost**: LUT‑basiert, beeinflusst Bilder & GIF‑Frames im Browser (Preview + Upload) und liegt in den Settings.【F:esp32Hub75/main.sketch†L151-L314】
- **Helligkeit**: Jeder Tab hat einen Helligkeits‑Regler, der die Panel‑Helligkeit per WebSocket `bright` steuert.【F:esp32Hub75/main.sketch†L386-L694】【F:esp32Hub75/main.sketch†L802-L835】
- **Uhr/Stopuhr**: NTP‑Uhr (HH:MM/HH:MM:SS) oder Stopuhr (HH:MM:SS) inkl. LED‑Kette, die pro Minute einmal den Panel‑Rand umläuft; bei exakt einer Minute erscheint ein kompletter Rahmen; Farbe im UI einstellbar.【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1287-L1408】
- **Uhrfarbe**: Uhrfarbe und Uhr‑Helligkeit lassen sich im UI separat einstellen (wirkt nur auf die Uhrzeit).【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1468-L1515】
- **Wetter (Koblenz)**: Im Uhr‑Modus optional Temperatur mit 16×16‑Icon (links unten) und Temperatur rechts unten anzeigen, Uhr bleibt in der oberen Hälfte.【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1302-L1458】
- **Bild‑Mapping**: Bild‑Upload folgt derselben Canvas‑Mapping‑Pipeline wie GIFs (Image → Canvas → 64×32) und wird anschließend wie ein GIF‑Frame als `anim.bin` gepackt, hochgeladen und lokal vom ESP32 gerendert. 【F:esp32Hub75/main.sketch†L535-L799】
- **Panel‑Redraw**: Button „Redraw Panel“ packt die aktuelle Pixelart als Single‑Frame‑`anim.bin` und lässt den ESP32 das Bild lokal anzeigen (wie bei GIFs), wodurch Unterbrechungen durch UI‑Jobs vermieden werden. 【F:esp32Hub75/main.sketch†L69-L799】
- **Pixelart Save/Load**: Lokales Speichern/Laden im Browser (LocalStorage) mit versioniertem Format und Größenprüfung, ohne Server‑Roundtrip. 【F:esp32Hub75/main.sketch†L1066-L1113】
- **WLED‑ähnliche Effekte**: Eigener UI‑Bereich mit Start/Stop, Speed/Intensity sowie Effekt‑Parametern (Matrix, Blink, Colorfading, Rainbow, Kaminfeuer, Twinkle, Scanner, Waves).【F:esp32Hub75/main.sketch†L58-L1684】

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
  - `{"t":"fx","mode":"matrix","run":1,"speed":80,"intensity":180,"density":120,"trail":180,"duty":160,"dir":1,"cooling":120,"sparks":120,"c1":0x00FF00,"c2":0xFF0000}` – WLED‑ähnliche Effekte starten/parametrieren.【F:esp32Hub75/main.sketch†L94-L1149】
  - `{"t":"mode","mode":"clock"}` – Display‑Modus setzen (`ui`, `clock`, `stopwatch`).【F:esp32Hub75/main.sketch†L1688-L1797】
  - `{"t":"clockfmt","fmt":"hhmm"}` – Uhrformat wählen (`hhmm` oder `hhmmss`).【F:esp32Hub75/main.sketch†L1688-L1797】
  - `{"t":"clock","c":0xFFFFFF,"i":255}` – Uhrfarbe (RGB) und Uhr‑Helligkeit (10–255) setzen.【F:esp32Hub75/main.sketch†L1872-L1905】
  - `{"t":"weather","on":1}` – Wetter‑Overlay im Uhr‑Modus aktivieren/deaktivieren.【F:esp32Hub75/main.sketch†L1688-L1802】
  - `{"t":"stopwatch","run":1,"reset":0,"ring":0x00FF00}` – Stopuhr steuern und LED‑Kettenfarbe setzen.【F:esp32Hub75/main.sketch†L1688-L1797】

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

### Pixelart‑Editor: Load/Save auf Client

- **Export**: Pixelart als JSON vom Browser herunterladen (Datei auf dem Client speichern).
- **Import**: JSON vom Client laden und als Pixelart ins Canvas + Panel übertragen.

### Animationen im Stil von WLED

Umgesetzt ist ein eigener Animations‑Bereich mit Parametern pro Effekt:

- **Matrix Kino‑Film** (Digit‑Regen mit Trails): Parameter z. B. Geschwindigkeit, Dichte, Trail‑Länge, Farbpalette/Grün‑Tint.
- **Blink**: Parameter z. B. Geschwindigkeit, Duty‑Cycle, Farbpalette, zufällige Startphasen.
- **Colorfading**: Parameter z. B. Fade‑Speed, Farbpalette, Loop‑Modus.
- **Rainbow**: Parameter z. B. Geschwindigkeit, Richtung, Sättigung/Intensität.
- **Kaminfeuer**: Parameter z. B. Flammenhöhe, Glut‑Intensität, Flacker‑Stärke, Farbpalette.
- **Twinkle**: Parameter z. B. Dichte, Speed, Intensität/Farbe.
- **Scanner**: Parameter z. B. Speed, Breite/Trail, Richtung, Farbe.
- **Waves**: Parameter z. B. Speed, Richtung, Intensität.
Status: umgesetzt (Effekt‑Engine + UI‑Steuerung im Sketch).【F:esp32Hub75/main.sketch†L58-L1684】

## Taskliste (Nächste notwendige Aufgaben)

Basierend auf den dokumentierten Einschränkungen und Optional‑Features ergeben sich folgende nächste Schritte:

1. **Presets für Pixelart/Bilder**: Speichern/Laden in LittleFS integrieren (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L777-L805】
2. **Animation‑Builder im UI**: Pixelart‑Frames erfassen und als Animation exportieren (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L90-L377】
3. **Umsetzungs‑Task Animationen**: Effekt‑Engine + Effekte inkl. UI‑Parametersteuerung (umgesetzt in `main.sketch`, siehe `tasks.md`, Abschnitt B0).

## Aufgaben zur Umsetzung (Roadmap‑Features)

### Pixelart‑Editor: Load/Save auf Client

1. **JSON‑Schema definieren**: 64×32 Pixel als Array (RGB888), Metadaten (Version, Breite/Höhe). Quelle: `README.md` (Roadmap), `main.sketch` (Framebuffer‑Format).
2. **Export‑Button in UI**: Aktuelle Pixelart aus `pix[]` in JSON serialisieren und als Datei herunterladen. Quelle: `main.sketch` (UI/JS).
3. **Import‑Flow in UI**: JSON vom Client laden, validieren (Größe/Version), Pixel ins Canvas schreiben und per `px`/`fill` ans Panel übertragen. Quelle: `main.sketch` (WebSocket `px`).
4. **Fehlerhandling**: UI‑Meldungen bei ungültigem JSON/Format; optional Vorschau vor Senden. Quellen: `main.sketch` (UI/JS), `README.md`.

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
