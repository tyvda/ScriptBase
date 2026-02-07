# How‑To: Aufgaben rund um ESP32 HUB75

Dieses Dokument sammelt kurze Rezepte für typische Aufgaben mit dem Sketch in `main.sketch`.【F:esp32Hub75/main.sketch†L1-L904】

## Überblick

Der ESP32 stellt lokal eine Web‑UI, Upload‑Workflows für Bilder/GIFs sowie eine Animation‑Engine bereit und steuert das HUB75‑Panel direkt per I2S DMA – ohne externe Server.【F:esp32Hub75/main.sketch†L1-L904】

Hinweis: Die Web‑UI ist im hellen Teenage‑Engineering‑Look mit Kartenlayout und Mono‑Typografie gestaltet; die Farbpalette und das feine Canvas‑Grid trennen die Pixel klar, die Zeichenfläche ist intern 64×32 und wird nur optisch skaliert.【F:esp32Hub75/main.sketch†L92-L412】

## Tabs wechseln

Die UI ist in Tabs aufgeteilt: **Uhr**, **Stopuhr**, **Pixelart** und **Animationen**. Beim Wechsel des Tabs wird der passende Display‑Modus gesetzt (z. B. Uhr‑Modus im Uhr‑Tab).【F:esp32Hub75/main.sketch†L419-L736】【F:esp32Hub75/main.sketch†L1086-L1132】

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

## Pixelart speichern/laden (Browser)

Die Buttons **Save** und **Load** speichern die aktuelle Pixelart lokal im Browser (LocalStorage) in einem versionierten Format mit Größenprüfung und laden sie wieder. Nach dem Laden kannst du mit „Redraw Panel“ erneut ans Panel senden.【F:esp32Hub75/main.sketch†L1066-L1161】

## Pixelart JSON exportieren/importieren

- **Export JSON** lädt eine Datei mit `version`, `width`, `height`, `pixels` herunter.
- **Import JSON** prüft das Schema (64×32, Array‑Länge) und übernimmt die Pixel ins Canvas.

Das JSON‑Format ist versioniert und wird vor dem Import validiert.【F:esp32Hub75/main.sketch†L1324-L1536】

## Frames im Pixelart‑Tab

- **Next Frame** zeigt das nächste Frame an.
- **+ Frame** ergänzt weitere Frames (z. B. für neue Animations‑Schritte).
- Ohne GIF wird der aktuelle Frame beim Wechsel kopiert, damit du sofort weiterzeichnen kannst.

Das ist die Basis für Pixelart‑Sequenzen im Editor.【F:esp32Hub75/main.sketch†L452-L692】【F:esp32Hub75/main.sketch†L1133-L1199】

## Frame‑Animation starten

1. Frames im Pixelart‑Tab vorbereiten.
2. **Animation starten** baut `anim.bin` aus den Frames und startet die Wiedergabe.
3. **Animation stoppen** beendet die Wiedergabe.

Der Ablauf nutzt die Frame‑Liste aus dem Pixelart‑Tab.【F:esp32Hub75/main.sketch†L486-L611】【F:esp32Hub75/main.sketch†L1696-L1744】

## Presets in LittleFS (Pixelart + Animation)

1. Preset‑Namen vergeben (z. B. `logo-1`).
2. **Pixelart sichern** speichert das aktuelle Canvas als JSON in LittleFS.
3. **Pixelart laden** holt das Preset zurück ins Canvas.
4. **Animation sichern** speichert die letzte anim.bin (GIF/Builder/Pixelart) als Preset.
5. **Animation laden** lädt das Preset und startet die Wiedergabe.

Die Presets werden serverseitig über `/api/preset/pixelart` und `/api/preset/anim` gespeichert bzw. geladen.【F:esp32Hub75/main.sketch†L408-L520】【F:esp32Hub75/main.sketch†L2718-L2850】

### Presets auswählen & JSON downloaden

- **Preset‑Listen** zeigen die Inhalte aus LittleFS.
- **Download JSON** lädt das ausgewählte Pixelart‑Preset als Datei.
- **JSON → Preset** importiert eine JSON‑Datei in LittleFS.

So kannst du Presets extern sichern oder wieder einspielen.【F:esp32Hub75/main.sketch†L502-L520】【F:esp32Hub75/main.sketch†L1683-L1764】

## Animation‑Builder (Pixelart‑Frames)

- **Frame hinzufügen** sammelt die aktuelle Pixelart als Frame.
- **Frame‑Delay** definiert die Verzögerung pro Frame (20–1000 ms).
- **Anim bauen & senden** erzeugt eine anim.bin und spielt sie direkt ab.

So kannst du kurze Pixelart‑Sequenzen ohne externes Tool erstellen.【F:esp32Hub75/main.sketch†L520-L1561】

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

Beim GIF‑Prepare wird das erste Frame in die Canvas geladen, sodass es direkt als Pixelart‑Frame weiterbearbeitet werden kann.【F:esp32Hub75/main.sketch†L1841-L1894】

## GIF‑Frames als Pixelart‑JSON exportieren

1. GIF auswählen.
2. **Prepare & Upload** ausführen (Frames werden dekodiert und gemappt).
3. **Export Frames** speichert ein JSON mit `frames` (Pixelart‑Arrays + `delayMs`).

So lassen sich einzelne Frames später als Pixelart weiterverwenden oder archivieren.【F:esp32Hub75/main.sketch†L1824-L1884】

## WLED‑ähnliche Effekte starten

Die UI bietet einen eigenen Bereich für Effekte (Matrix, Kaminfeuer). Andere Effekte sind vorerst deaktiviert. Start/Stop und Parameter werden per WebSocket gesteuert:

```json
{"t":"fx","mode":"matrix","run":1,"speed":80,"intensity":180,"density":120,"trail":180,"cooling":120,"sparks":120,"c1":65280}
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
5. **Uhrfarbe**: Farbe und Helligkeit der Uhr per UI einstellen (wirkt nur auf die Uhrzeit).
6. **LED‑Kette**: Farbe per Farbwähler einstellen; die Kette läuft in einer Minute einmal um den Panel‑Rand (Start oben links → oben rechts → unten rechts → unten links). Bei exakt einer Minute erscheint ein kompletter Rahmen.【F:esp32Hub75/main.sketch†L252-L340】【F:esp32Hub75/main.sketch†L1462-L1566】

Zeitbezug erfolgt über NTP (`pool.ntp.org`) und TZ‑Info im Sketch. Wetterdaten kommen von `WEATHER_URL` (Open‑Meteo, Standort Koblenz).【F:esp32Hub75/main.sketch†L16-L25】【F:esp32Hub75/main.sketch†L1499-L1542】【F:esp32Hub75/main.sketch†L1924-L1927】

### Display‑Schlafzeit nutzen

Der Sketch enthält einen Zeitplan, der das Display innerhalb eines Zeitfensters automatisch dunkel schaltet (z. B. nachts). Die Umschaltung erfolgt auf Basis der NTP‑Zeit und greift dadurch auch nach einem Neustart, sobald die Uhrzeit synchron ist. Konfiguration in `main.sketch`:

```cpp
static bool sleepEnabled = true;
static uint8_t sleepStartHour = 23;
static uint8_t sleepStartMinute = 0;
static uint8_t sleepEndHour = 6;
static uint8_t sleepEndMinute = 0;
static uint8_t sleepDimPercent = 10;
```
【F:esp32Hub75/main.sketch†L19-L36】【F:esp32Hub75/main.sketch†L836-L886】

Die Web‑UI ist die primäre Konfiguration und speichert die Schlafzeit in LittleFS, sodass sie nach Stromausfall erhalten bleibt. `sleepDimPercent` steuert die Helligkeit im Schlafmodus zwischen 0–20 % (0 % = aus); die Uhr läuft weiter, auch wenn das Panel dunkel ist.【F:esp32Hub75/main.sketch†L19-L36】【F:esp32Hub75/main.sketch†L2198-L2268】【F:esp32Hub75/main.sketch†L2638-L2690】

## Implementierungscheck (Sketch-Abgleich)

Die How‑To‑Rezepte entsprechen den implementierten Endpoints, WebSocket‑Formaten und der Animation‑Pipeline im Sketch.【F:esp32Hub75/main.sketch†L62-L739】【F:esp32Hub75/main.sketch†L827-L862】

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

Die umfassende Aufgabenbeschreibung befindet sich in `tasks.md`.【F:esp32Hub75/tasks.md†L1-L99】
