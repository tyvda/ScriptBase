# Tutorial: ESP32 HUB75 64×32 Panel in Betrieb nehmen

Dieses Tutorial führt Schritt für Schritt durch Konfiguration, Flash und Nutzung der Web‑UI. Alle Angaben basieren auf `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Das Projekt ist ein lokaler LED‑Matrix‑Controller für ein HUB75‑Panel (64×32, 1/16 Scan) auf ESP32‑Basis. Es bietet eine Web‑UI mit Pixel‑Editor, Bild‑Upload und GIF‑Animation – ohne Cloud‑Zwang oder externen Server.【F:esp32Hub75/main.sketch†L1-L904】

Die Oberfläche ist modern und klar im Teenage‑Engineering‑Stil aufgebaut (helles Kartenlayout, Mono‑Typografie, prägnante Status‑Pills).【F:esp32Hub75/main.sketch†L167-L412】

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

Die UI ist in Tabs strukturiert: **Uhr**, **Stopuhr**, **Pixelart**, **Animationen**. Der aktive Tab setzt den Display‑Modus automatisch passend.【F:esp32Hub75/main.sketch†L419-L736】【F:esp32Hub75/main.sketch†L1086-L1132】

## 7) Pixel‑Zeichnen

- Linksklick malt mit Farbe.
- Rechtsklick löscht (schwarz).
- Brush‑Größe 1×1 bis 4×4.
- `Clear` leert das Panel, `Fill` füllt alles mit der aktuellen Farbe.【F:esp32Hub75/main.sketch†L90-L365】
- Das Canvas zeigt ein feines Grid zur optischen Pixeltrennung.【F:esp32Hub75/main.sketch†L92-L105】
- Die Farbpalette setzt die aktive Zeichenfarbe; das Canvas ist intern 64×32 und wird nur optisch skaliert.【F:esp32Hub75/main.sketch†L120-L356】
- `Reinit` initialisiert das Display neu und löscht die Canvas/Panel‑Daten (Pixelart startet sauber neu).【F:esp32Hub75/main.sketch†L368-L377】【F:esp32Hub75/main.sketch†L820-L825】
- Der Button „Redraw Panel“ packt die aktuelle Pixelart als Single‑Frame‑`anim.bin` und lässt den ESP32 sie lokal wie ein GIF rendern (keine `px`‑Flut, keine Unterbrechung durch UI‑Aktionen).【F:esp32Hub75/main.sketch†L69-L799】
- **Save/Load** speichert die Pixelart lokal im Browser (LocalStorage) als versioniertes Format mit Größenprüfung und lädt sie wieder in das Canvas.【F:esp32Hub75/main.sketch†L1066-L1161】
- **Export JSON** lädt die Pixelart als JSON herunter, **Import JSON** lädt validierte JSONs zurück in das Canvas.【F:esp32Hub75/main.sketch†L1324-L1536】
- **Presets (LittleFS)**: Pixelart/Animationen können im Gerät gespeichert und später geladen werden (Preset‑Name vergeben).【F:esp32Hub75/main.sketch†L408-L520】
- **Preset‑Listen**: Gespeicherte Presets lassen sich auswählen und laden; JSON kann heruntergeladen oder importiert werden.【F:esp32Hub75/main.sketch†L502-L520】
- **Animation‑Builder**: Frames aus der Pixelart sammeln, Delay/Loop setzen und als anim.bin senden.【F:esp32Hub75/main.sketch†L520-L1561】
- **Frames**: Next Frame springt weiter, + Frame ergänzt zusätzliche Frames für Sequenzen.【F:esp32Hub75/main.sketch†L452-L692】
- **Animation starten**: Im Pixelart‑Tab wird aus Frames eine anim.bin gebaut und abgespielt.【F:esp32Hub75/main.sketch†L486-L611】

## 7.1) Helligkeit einstellen

Im Bereich "Bild / GIF Tuning" steht ein Helligkeits‑Regler zur Verfügung. Dieser steuert die Panel‑Helligkeit direkt per WebSocket (`bright`).【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】

## 7.2) Uhr & Stopuhr (NTP)

Der Bereich **Uhr / Stopuhr (NTP)** steuert die Zeitdarstellung:

- **Modus**: `Uhr`, `Stopuhr` oder `Canvas & Media`.
- **Uhrformat**: `HH:MM` oder `HH:MM:SS` (Uhrzeit kommt per NTP).
- **Stopuhr**: Start/Stop/Reset; Anzeige `HH:MM:SS`.
- **Wetter (Koblenz)**: Toggle aktivieren, damit unten links ein 16×16‑Icon und rechts daneben die Temperatur erscheint (Uhr bleibt oben).
- **Uhrfarbe**: Farbe und Helligkeit der Uhrzeit im UI einstellen.
- **LED‑Kette**: Farbe einstellen – die Kette umrundet den Rand in einer Minute (Start oben links → oben rechts → unten rechts → unten links). Bei exakt einer Minute erscheint ein kompletter Rahmen.【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1363-L1408】

Die Zeitsynchronisation nutzt `pool.ntp.org` und die TZ‑Info aus der User‑Config (`TZ_INFO`). Wetterdaten kommen von `WEATHER_URL` (Open‑Meteo, Standort Koblenz).【F:esp32Hub75/main.sketch†L16-L25】【F:esp32Hub75/main.sketch†L1499-L1542】【F:esp32Hub75/main.sketch†L1924-L1927】

Für Winterzeit/Sommerzeit in Deutschland ist `TZ_INFO` auf `CET/CEST` gesetzt. Bei anderem Standort die Zeitzone anpassen.【F:esp32Hub75/main.sketch†L19-L25】

### 7.3) Display‑Schlafzeit konfigurieren

Das Panel kann automatisch innerhalb eines Zeitfensters abgeschaltet werden (z. B. nachts). Der Zeitplan basiert auf der NTP‑Zeit und greift auch nach einem Neustart:

```cpp
static bool sleepEnabled = true;
static uint8_t sleepStartHour = 23;
static uint8_t sleepStartMinute = 0;
static uint8_t sleepEndHour = 6;
static uint8_t sleepEndMinute = 0;
static uint8_t sleepDimPercent = 10;
```
【F:esp32Hub75/main.sketch†L19-L36】【F:esp32Hub75/main.sketch†L836-L886】

Die Web‑UI ist die primäre Konfiguration und speichert die Schlafzeit in LittleFS, sodass sie nach Stromausfall erhalten bleibt. `sleepDimPercent` definiert die Schlaf‑Helligkeit zwischen 0–20 % (0 % = aus); die Uhr läuft weiter, auch wenn das Panel dunkel ist.【F:esp32Hub75/main.sketch†L19-L36】【F:esp32Hub75/main.sketch†L2198-L2268】【F:esp32Hub75/main.sketch†L2638-L2690】

## 8) Bild senden

1. PNG/JPG/WebP auswählen.
2. Optional Aspect (Auto/4:3/16:9) und Mapping (Cover/Contain) wählen.
3. `Preview` zeichnet in die UI, `Send to Panel` packt das Bild als Single‑Frame‑`anim.bin` (wie GIF‑Frames) und lässt den ESP32 das Bild lokal rendern.【F:esp32Hub75/main.sketch†L142-L799】
   Die Bildpipeline zeichnet das Original zuerst auf ein Canvas und mappt dann auf 64×32 (gleiches Mapping wie bei GIFs).【F:esp32Hub75/main.sketch†L535-L590】

## 9) GIF vorbereiten & abspielen

1. GIF auswählen.
2. `Prepare & Upload` erstellt `anim.bin` im Browser und lädt es hoch (max. 50 Frames).
3. `Play` startet die Animation, `Stop` stoppt sie.
4. Optional: `Export Frames` lädt die GIF‑Frames als Pixelart‑JSON.

Das erste Frame wird in die Canvas geladen, sodass du es direkt als Pixelart‑Frame weiterverwenden kannst. Die GIF‑Dekodierung nutzt `gifuct-js` via CDN.【F:esp32Hub75/main.sketch†L222-L612】

## 10) WLED‑ähnliche Effekte starten

Im UI‑Bereich „WLED‑ähnliche Animationen“ kannst du aktuell Matrix und Kaminfeuer starten. Weitere Effekte sind vorerst deaktiviert. Parameter wirken live (Speed, Intensity usw.). Start/Stop und Parameteränderungen werden via WebSocket übertragen.【F:esp32Hub75/main.sketch†L58-L1684】

## Implementierungscheck (Sketch-Abgleich)

Die im Tutorial beschriebenen Funktionen (HUB75‑Betrieb, Pixelart, Bild‑Upload, GIF‑Import) sind im aktuellen Sketch enthalten und können direkt über die Web‑UI und Endpoints genutzt werden.【F:esp32Hub75/main.sketch†L13-L862】

## Zukünftige Features (Roadmap)

### Pixelart‑Editor: Load/Save auf Client

Feature ist umgesetzt (JSON‑Export/Import im Browser).

### Preset‑Management in der UI

- Preset‑Liste anzeigen, umbenennen und löschen.
- Optional: Preview pro Preset.

### Animationen im Stil von WLED (Matrix + Kaminfeuer aktiv)

- **Matrix Kino‑Film** (Digit‑Regen mit Trails): Parameter z. B. Geschwindigkeit, Dichte, Trail‑Länge, Farbpalette/Grün‑Tint.
- **Kaminfeuer**: Parameter z. B. Flammenhöhe, Glut‑Intensität, Flacker‑Stärke, Farbpalette.
Weitere Effekte (Blink, Colorfading, Rainbow, Twinkle, Scanner, Waves) sind aktuell deaktiviert.
Status: umgesetzt; aktuell sind Matrix und Kaminfeuer aktiv, weitere Effekte sind deaktiviert.【F:esp32Hub75/main.sketch†L58-L1684】

## Taskliste (Nächste notwendige Aufgaben)

1. **Preset‑Verwaltung**: Preset‑Liste, Umbenennen/Löschen, optional Vorschau.
2. **Multi‑Panel Support**: Chain > 1 inkl. Layout/Mapping.
3. **MQTT/REST API**: Externe Steuerung für Automationen/Installationen.

## Aufgaben zur Umsetzung (Roadmap‑Features)

### Pixelart JSON Export/Import

- **Status**: umgesetzt (Export/Import im Browser).

### Preset‑Management in der UI

1. **Preset‑Liste**: Verfügbare Presets aus LittleFS anzeigen.
2. **Löschen/Umbenennen**: Presets verwalten (UI‑Flow, Bestätigungen).
3. **Preview**: Optional Thumbnail aus erster Frame‑Zeile generieren.

### Animation‑Builder (Pixelart)

- **Status**: umgesetzt (Frame‑Liste → anim.bin).

### WLED‑ähnliche Animationen

1. **Effekt‑Engine abstrahieren** (Frame‑Tick, Parameter).
2. **Matrix Kino‑Film**: Digit‑Regen mit Trails (Speed, Density, Trail‑Length, Palette).
3. **Blink**: On/Off‑Pattern (Speed, Duty‑Cycle, Palette, Random Seed) – vorerst deaktiviert.
4. **Colorfading**: Interpolation (Fade‑Speed, Palette, Loop) – vorerst deaktiviert.
5. **Rainbow**: HSV‑Sweep (Speed, Direction, Saturation/Intensity) – vorerst deaktiviert.
6. **Kaminfeuer**: Heat‑Map/Convolution (Flame Height, Glow, Flicker, Palette).
7. **UI‑Parametersteuerung**: Dropdown + Slider, Live‑Update via WebSocket JSON.
8. **Persistenz optional**: Letzten Effekt/Parameter in LittleFS speichern.

Die vollständige Aufgabenliste steht in `tasks.md`.【F:esp32Hub75/tasks.md†L1-L99】
