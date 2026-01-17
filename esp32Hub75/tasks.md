# Tasks: Umsetzung Roadmap‑Features (ESP32 HUB75)

Diese Aufgabenliste beschreibt detailliert die Umsetzung der geplanten Roadmap‑Features. Sie ist so strukturiert, dass Implementierungen im Code und in der Doku eindeutig auf einzelne Aufgaben zurückgeführt werden können.

## Kontext & Ziele

- **Pixelart‑Editor Load/Save**: JSON‑Export/Import direkt auf dem Client (Browser), damit Nutzer ihre Pixelart lokal speichern und wieder laden können.
- **WLED‑ähnliche Animationen**: Effekt‑Engine + parametrierbare Effekte (Matrix Kino‑Film, Blink, Colorfading, Rainbow, Kaminfeuer).

## A) Pixelart‑Editor: Load/Save auf Client

### A1) JSON‑Schema & Validierung

- **Format definieren**:
  - `version` (int) für zukünftige Schemaänderungen.
  - `width`, `height` (erwartet 64×32).
  - `pixels` als 1D‑Array RGB888 (`0xRRGGBB`) oder als Array `{r,g,b}`.
- **Validierung**:
  - Prüfe `width*height === pixels.length`.
  - Wertebereich 0x000000–0xFFFFFF.
  - Optional: Schema‑Migration bei `version`.

### A2) Export (Download)

- **UI‑Button hinzufügen**: „Export JSON“.
- **Serialisierung**: `pix[]` → JSON.
- **Download**: Client‑seitig als Datei speichern (Blob + `a.download`).
- **Dateinamen**: z. B. `pixelart-64x32-YYYYMMDD-HHMMSS.json`.

### A3) Import (Upload)

- **UI‑Input hinzufügen**: „Import JSON“ (File Input).
- **Parsing & Validierung**: Schema prüfen, Fehler melden.
- **Render‑Flow**:
  - Canvas aktualisieren.
  - Panel via `px`‑Updates/`fill` neu zeichnen.
- **Fehlerhandling**:
  - Fehlermeldung bei invalidem JSON/Schema.
  - Optional: Preview vor Senden.

### A4) Dokumentation & API‑Hinweise

- Update `README.md`, `HOWTO.md`, `TUTORIAL.md` mit Import/Export‑Workflow.
- Verweis auf JSON‑Schema (hier dokumentiert).

## B) WLED‑ähnliche Animationen

### B0) Umsetzungs‑Task: Effekt‑Engine + Effekte (Sprint‑Story)

- **Ziel**: WLED‑ähnliche Animationen als integrierten Modus im Sketch bereitstellen.
- **Scope**:
  - Effekt‑Engine (Registry + Tick‑Loop + Parameter‑Schema).
  - Effekte B2–B6 implementieren.
  - UI‑Steuerung (Dropdown + Slider) inkl. Live‑Update via WebSocket‑JSON.
- **Akzeptanzkriterien**:
  - Start/Stop per WebSocket‑JSON möglich.
  - Parameteränderungen wirken live ohne Neustart.
  - Standard‑Preset pro Effekt ist dokumentiert.
- **Status**: umgesetzt in `main.sketch` inkl. UI‑Bereich, WebSocket‑Steuerung und Effekt‑Logik.

### B1) Effekt‑Engine (Framework)

- **Loop‑Integration**: Effekt‑Tick im `loop()`.
- **Parameter‑Schema**:
  - Gemeinsame Parameter (Speed, Palette, Intensity).
  - Effekt‑spezifische Parameter (z. B. Trail‑Länge, Duty‑Cycle).
- **Effekt‑Registry**: Auswahl per Name/ID.
- **Stop/Start**: Effekt via WebSocket‑JSON steuern.

### B2) Matrix Kino‑Film

- **Algorithmus**: Digit‑Regen mit Trail‑Decay.
- **Parameter**: Geschwindigkeit, Dichte, Trail‑Länge, Farbpalette (Grün‑Tint).
- **Render‑Pfad**: Framebuffer‑Update pro Tick.

### B3) Blink

- **Algorithmus**: On/Off‑Zyklus mit optionaler Randomisierung.
- **Parameter**: Geschwindigkeit, Duty‑Cycle, Farbpalette, Random Seed.

### B4) Colorfading

- **Algorithmus**: Interpolation zwischen Farben.
- **Parameter**: Fade‑Speed, Palette, Loop‑Modus.

### B5) Rainbow

- **Algorithmus**: HSV‑Sweep über die Matrix.
- **Parameter**: Speed, Direction, Saturation/Intensity.

### B6) Kaminfeuer

- **Algorithmus**: Heat‑Map mit Diffusion/Convolution.
- **Parameter**: Flammenhöhe, Glut‑Intensität, Flacker‑Stärke, Palette.

### B9) Twinkle (neu)

- **Algorithmus**: Zufällige Sternchen mit Fade‑Out.
- **Parameter**: Dichte, Geschwindigkeit, Farbe/Intensität.

### B10) Scanner (neu)

- **Algorithmus**: Wandernder Balken mit Trail (Cylon‑Effekt).
- **Parameter**: Geschwindigkeit, Breite/Trail, Farbe, Richtung.

### B11) Waves (neu)

- **Algorithmus**: Sinus‑Wellen mit HSV‑Farbverlauf.
- **Parameter**: Geschwindigkeit, Richtung, Intensität.

### B7) UI‑Steuerung

- **UI‑Bereich**: Dropdown für Effekt, Slider für Parameter.
- **Live‑Update**: Parameter via WebSocket‑JSON senden.
- **Preset‑Handling (optional)**: Parameter‑Sets speichern/laden.

### B8) Persistenz (optional)

- Speicherung letzter Effekt/Parameter in LittleFS (z. B. `/effect.json`).

## C) Qualität & Wartung

- **Error‑Handling**: klare Fehlermeldungen im UI.
- **Performance**: effiziente Framebuffer‑Updates (nur geänderte Pixel).
- **Dokumentation**: Änderungen in `changelog.md` mit Quellenbezug.
