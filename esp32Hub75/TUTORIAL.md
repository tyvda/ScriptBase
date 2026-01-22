# Tutorial: ESP32 HUB75 64×32 Panel in Betrieb nehmen

Dieses Tutorial führt Schritt für Schritt durch Konfiguration, Flash und Nutzung der Web‑UI. Alle Angaben basieren auf `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Das Projekt ist ein lokaler LED‑Matrix‑Controller für ein HUB75‑Panel (64×32, 1/16 Scan) auf ESP32‑Basis. Es bietet eine Web‑UI mit Pixel‑Editor, Bild‑Upload und GIF‑Animation – ohne Cloud‑Zwang oder externen Server.【F:esp32Hub75/main.sketch†L1-L904】

Die Oberfläche ist modern und klar im Teenage‑Engineering‑Stil aufgebaut (helles Kartenlayout, Mono‑Typografie, prägnante Status‑Pills). Die Menüs sind oben als Symbol‑Tabs organisiert (Uhr, Pixelart, Anzeige, Animation, Settings).【F:esp32Hub75/main.sketch†L167-L694】

## 1) WLAN & mDNS konfigurieren

Im Sketch die Zugangsdaten anpassen:

```cpp
static const char* WIFI_SSID = "DEIN_SSID";
static const char* WIFI_PASS = "DEIN_PASS";
static const char* MDNS_NAME = "hub75";
```
【F:esp32Hub75/main.sketch†L19-L21】

## 2) Panel‑Parameter prüfen

Stelle sicher, dass Auflösung und Chain‑Länge zum Panel passen:

```cpp
#define PANEL_RES_X 64
#define PANEL_RES_Y 32
#define PANEL_CHAIN 1
```
【F:esp32Hub75/main.sketch†L26-L28】

## 3) Pin‑Mapping anpassen (falls nötig)

Die `HubPins` Struktur enthält das Mapping. Wenn dein Panel‑Adapter abweicht, passe die Pins an.

```cpp
struct HubPins {
  int r1=25,g1=26,b1=27;
  int r2=14,g2=33,b2=32;

  int a=23,b=19,c=5,d=17,e=-1;

  int clk=16, lat=4, oe=21;

  HUB75_I2S_CFG::shift_driver driver = HUB75_I2S_CFG::SHIFTREG;
  bool clkphase = true;
  bool double_buff = false;
};
```
【F:esp32Hub75/main.sketch†L33-L45】

## 4) Hardware anschließen

- Panel: 5V externe Versorgung.
- ESP32: USB oder 5V.
- GND von Panel und ESP32 verbinden.

Das Pin‑Mapping entspricht den Werten in `HubPins`.【F:esp32Hub75/main.sketch†L33-L47】

## 5) Sketch flashen

- Mit Arduino IDE/PlatformIO kompilieren.
- Sketch auf den ESP32 flashen.
- Serielle Ausgabe beobachten (IP‑Adresse).【F:esp32Hub75/main.sketch†L797-L805】

## 6) Web‑UI öffnen

Im Browser:

- `http://<ip>/` oder
- `http://hub75.local/` (mDNS)

Die UI wird vom ESP32 ausgeliefert.【F:esp32Hub75/main.sketch†L815-L818】

Falls der WebSocket‑Status in der UI auf „connecting…“ stehen bleibt, Browser‑Konsole prüfen und ggf. Cache leeren oder die aktuelle Firmware erneut flashen.【F:esp32Hub75/main.sketch†L242-L536】

## 7) Pixel‑Zeichnen

Öffne den Tab **Pixelart**, um den Editor zu sehen.

- Linksklick malt mit Farbe.
- Rechtsklick löscht (schwarz).
- Brush‑Größe 1×1 bis 4×4.
- `Clear` leert das Panel, `Fill` füllt alles mit der aktuellen Farbe.【F:esp32Hub75/main.sketch†L90-L365】
- Das Canvas zeigt ein feines Grid zur optischen Pixeltrennung.【F:esp32Hub75/main.sketch†L92-L105】
- Die Farbpalette setzt die aktive Zeichenfarbe; das Canvas ist intern 64×32 und wird nur optisch skaliert.【F:esp32Hub75/main.sketch†L120-L356】
- `Reinit` initialisiert das Display neu und löscht die Canvas/Panel‑Daten (Pixelart startet sauber neu).【F:esp32Hub75/main.sketch†L368-L377】【F:esp32Hub75/main.sketch†L820-L825】
- Der Button „Redraw Panel“ packt die aktuelle Pixelart als Single‑Frame‑`anim.bin` und lässt den ESP32 sie lokal wie ein GIF rendern (keine `px`‑Flut, keine Unterbrechung durch UI‑Aktionen).【F:esp32Hub75/main.sketch†L69-L799】
- **Save/Load** speichert die Pixelart lokal im Browser (LocalStorage) als versioniertes Format mit Größenprüfung und lädt sie wieder in das Canvas.【F:esp32Hub75/main.sketch†L1066-L1113】

## 7.1) Helligkeit einstellen

Jeder Tab enthält einen Helligkeits‑Regler. Er steuert die Panel‑Helligkeit direkt per WebSocket (`bright`).【F:esp32Hub75/main.sketch†L386-L835】

## 7.2) Uhr & Stopuhr (NTP)

Wechsle in den Tab **Uhr**. Dort steuert der Bereich **Uhr / Stopuhr (NTP)** die Zeitdarstellung:

- **Modus**: `Uhr`, `Stopuhr` oder `Canvas & Media`.
- **Uhrformat**: `HH:MM` oder `HH:MM:SS` (Uhrzeit kommt per NTP).
- **Stopuhr**: Start/Stop/Reset; Anzeige `HH:MM:SS`.
- **Wetter (Koblenz)**: Toggle aktivieren, damit unten links ein 16×16‑Icon und rechts daneben die Temperatur erscheint (Uhr bleibt oben).
- **Uhrfarbe**: Farbe und Helligkeit der Uhrzeit im UI einstellen.
- **LED‑Kette**: Farbe einstellen – die Kette umrundet den Rand in einer Minute (Start oben links → oben rechts → unten rechts → unten links). Bei exakt einer Minute erscheint ein kompletter Rahmen.【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1363-L1408】

Die Zeitsynchronisation nutzt `pool.ntp.org` und die TZ‑Info aus der User‑Config (`TZ_INFO`). Wetterdaten kommen von `WEATHER_URL` (Open‑Meteo, Standort Koblenz).【F:esp32Hub75/main.sketch†L16-L25】【F:esp32Hub75/main.sketch†L1499-L1542】【F:esp32Hub75/main.sketch†L1924-L1927】

## 8) Bild senden

Wechsle in den Tab **Anzeige**.
1. PNG/JPG/WebP auswählen.
2. Optional Aspect (Auto/4:3/16:9) und Mapping (Cover/Contain) wählen.
3. `Preview` zeichnet in die UI, `Send to Panel` packt das Bild als Single‑Frame‑`anim.bin` (wie GIF‑Frames) und lässt den ESP32 das Bild lokal rendern.【F:esp32Hub75/main.sketch†L142-L799】
   Die Bildpipeline zeichnet das Original zuerst auf ein Canvas und mappt dann auf 64×32 (gleiches Mapping wie bei GIFs).【F:esp32Hub75/main.sketch†L535-L590】

## 9) GIF vorbereiten & abspielen

Der GIF‑Upload befindet sich ebenfalls im Tab **Anzeige**.
1. GIF auswählen.
2. `Prepare & Upload` erstellt `anim.bin` im Browser und lädt es hoch (max. 50 Frames).
3. `Play` startet die Animation, `Stop` stoppt sie.

Die GIF‑Dekodierung nutzt `gifuct-js` via CDN.【F:esp32Hub75/main.sketch†L222-L612】

## 10) WLED‑ähnliche Effekte starten

Öffne den Tab **Animation**. Im UI‑Bereich „WLED‑ähnliche Animationen“ kannst du Effekte wie Matrix, Blink, Colorfading, Rainbow, Kaminfeuer, Twinkle, Scanner oder Waves starten. Parameter wirken live (Speed, Intensity usw.). Start/Stop und Parameteränderungen werden via WebSocket übertragen.【F:esp32Hub75/main.sketch†L58-L1684】

## Implementierungscheck (Sketch-Abgleich)

Die im Tutorial beschriebenen Funktionen (HUB75‑Betrieb, Pixelart, Bild‑Upload, GIF‑Import) sind im aktuellen Sketch enthalten und können direkt über die Web‑UI und Endpoints genutzt werden.【F:esp32Hub75/main.sketch†L13-L862】

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
Status: umgesetzt (Effekt‑Engine + UI‑Steuerung im Sketch).【F:esp32Hub75/main.sketch†L58-L1684】

## Taskliste (Nächste notwendige Aufgaben)

1. **Presets für Inhalte** in LittleFS ablegen (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L777-L805】
2. **Animation‑Builder** für Pixelart‑Sequenzen implementieren (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L90-L377】
3. **Umsetzungs‑Task Animationen**: Effekt‑Engine + Effekte inkl. UI‑Parametersteuerung (umgesetzt in `main.sketch`, siehe `tasks.md`, Abschnitt B0).

## Aufgaben zur Umsetzung (Roadmap‑Features)

### Pixelart‑Editor: Load/Save auf Client

1. **JSON‑Schema definieren**: 64×32 Pixel als Array (RGB888), Metadaten (Version, Breite/Höhe).
2. **Export‑Button in UI**: Pixelart aus `pix[]` als JSON speichern und herunterladen.
3. **Import‑Flow in UI**: JSON laden, validieren, Pixel ins Canvas schreiben und per `px` ans Panel senden.
4. **Fehlerhandling**: UI‑Meldungen + optional Vorschau.

### WLED‑ähnliche Animationen

1. **Effekt‑Engine abstrahieren** (Frame‑Tick, Parameter).
2. **Matrix Kino‑Film**: Digit‑Regen mit Trails (Speed, Density, Trail‑Length, Palette).
3. **Blink**: On/Off‑Pattern (Speed, Duty‑Cycle, Palette, Random Seed).
4. **Colorfading**: Interpolation (Fade‑Speed, Palette, Loop).
5. **Rainbow**: HSV‑Sweep (Speed, Direction, Saturation/Intensity).
6. **Kaminfeuer**: Heat‑Map/Convolution (Flame Height, Glow, Flicker, Palette).
7. **UI‑Parametersteuerung**: Dropdown + Slider, Live‑Update via WebSocket JSON.
8. **Persistenz optional**: Letzten Effekt/Parameter in LittleFS speichern.

Die vollständige Aufgabenliste steht in `tasks.md`.【F:esp32Hub75/tasks.md†L1-L99】
