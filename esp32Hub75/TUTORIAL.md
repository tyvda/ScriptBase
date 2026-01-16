# Tutorial: ESP32 HUB75 64×32 Panel in Betrieb nehmen

Dieses Tutorial führt Schritt für Schritt durch Konfiguration, Flash und Nutzung der Web‑UI. Alle Angaben basieren auf `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Das Projekt ist ein lokaler LED‑Matrix‑Controller für ein HUB75‑Panel (64×32, 1/16 Scan) auf ESP32‑Basis. Es bietet eine Web‑UI mit Pixel‑Editor, Bild‑Upload und GIF‑Animation sowie OTA‑Updates – ohne Cloud‑Zwang oder externen Server.【F:esp32Hub75/main.sketch†L1-L904】

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

## 7) Pixel‑Zeichnen

- Linksklick malt mit Farbe.
- Rechtsklick löscht (schwarz).
- Brush‑Größe 1×1 bis 4×4.
- `Clear` leert das Panel, `Fill` füllt alles mit der aktuellen Farbe.【F:esp32Hub75/main.sketch†L90-L365】

## 7.1) Helligkeit einstellen

Im Bereich "Bild / GIF Tuning" steht ein Helligkeits‑Regler zur Verfügung. Dieser steuert die Panel‑Helligkeit direkt per WebSocket (`bright`).【F:esp32Hub75/main.sketch†L160-L360】【F:esp32Hub75/main.sketch†L720-L768】

## 8) Bild senden

1. PNG/JPG/WebP auswählen.
2. Optional Aspect (Auto/4:3/16:9) und Mapping (Cover/Contain) wählen.
3. `Preview` zeichnet in die UI, `Send to Panel` überträgt das Frame (RGB565).【F:esp32Hub75/main.sketch†L142-L512】

## 9) GIF vorbereiten & abspielen

1. GIF auswählen.
2. `Prepare & Upload` erstellt `anim.bin` im Browser und lädt es hoch.
3. `Play` startet die Animation, `Stop` stoppt sie.

Die GIF‑Dekodierung nutzt `gifuct-js` via CDN.【F:esp32Hub75/main.sketch†L222-L612】

## 10) OTA Update

Im Browser `http://<ip>/update` öffnen und Firmware hochladen (ElegantOTA, Login über `OTA_USER`/`OTA_PASS`).【F:esp32Hub75/main.sketch†L860-L862】

## Implementierungscheck (Sketch-Abgleich)

Die im Tutorial beschriebenen Funktionen (HUB75‑Betrieb, Pixelart, Bild‑Upload, GIF‑Import und OTA) sind im aktuellen Sketch enthalten und können direkt über die Web‑UI und Endpoints genutzt werden.【F:esp32Hub75/main.sketch†L13-L862】

## Taskliste (Nächste notwendige Aufgaben)

1. **Presets für Inhalte** in LittleFS ablegen (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L777-L805】
2. **Animation‑Builder** für Pixelart‑Sequenzen implementieren (Nice‑to‑Have).【F:esp32Hub75/main.sketch†L90-L377】
