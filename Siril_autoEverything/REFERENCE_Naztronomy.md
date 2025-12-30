# Referenz: Naztronomy OSC Image Preprocessing Script

Dieses Dokument extrahiert die funktionalen Bausteine und die Architekturidee aus dem Beispielskript "Naztronomy - OSC Image Preprocessor" (PyQt6 + sirilpy). Es dient als Blaupause für unser eigenes Siril-Auto-Everything-Skript, ohne Lizenz- oder Autorangaben zu übernehmen.

## Funktions- und Architektur-Highlights
- **UI-Struktur (PyQt6)**: Tabs für Datei-Management, Sessions und Processing; Controls für Drizzle, Feathering, Filter-Roundness/FWHM sowie Preset-Speicherung und -Laden.
- **Siril-Anbindung (sirilpy)**: Verbindung, Versionsprüfung, Logging, Kommandobaukasten (`convert`, `stack`, `register`, `seqapplyreg`, `platesolve`, `seqplatesolve`, `calibrate`, `save`, `load`).
- **Session-Handling**: Mehrere Sessions mit getrennten Listen für Lights/Darks/Flats/Biases, Copy/Symlink nach Arbeitsordner, optional getrennte Verarbeitung und spätere Zusammenführung.
- **Kalibrierung & Stacking**: Umgang mit Einzel-Masterframes, Kalibration der Lights mit optionalem Debayering, Registrierung (2-pass, optional Drizzle), Feathering und Rejection-basierte Stacks.
- **Qualitätsfilter**: σ-Filter für Roundness und FWHM, Black-Frame-Erkennung, Plate-Solve-Fallback mit regulärer Registrierung, Logging der Entscheidungen.
- **Preset- und Dateimanagement**: JSON-basierte Presets inklusive Session-Dateilisten; benannte Exporte mit Header-Auswertung (OBJECT, EXPTIME etc.); optionales Aufräumen temporärer Ordner.
- **Mono-/Einzelsession-Workflows**: Separate Stapel je Session oder für monochrome Daten; registrierte Mono-Stapel werden gesammelt und können kombiniert werden.

## Ableitungen für unser Projekt
- **UI-Hooks**: Sliders/Checkboxes für Drizzle, Feather, Filter σ-Werte und Presets können direkt an Siril-Befehle angebunden werden.
- **Preset-Format**: JSON-Struktur mit Sessions und UI-States als Vorlage für unser Preset-Handling.
- **Qualitätsmetriken**: Roundness/FWHM-σ-Filter, Black-Frame-Scan und Plate-Solve-Fallback als Startpunkt für eigene QC-Logik.
- **Batch/Session-Strategie**: Copy/Symlink der Eingabeframes pro Session und spätere Merge-Logik für Multi-Session-Stapel.
- **Dateinamensschema**: Nutzung von Header-Daten (z. B. Objektname, Belichtungszeit, Stack-Count) für sprechende Exportnamen.
