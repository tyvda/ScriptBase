# Siril Auto-Everything (Deep-Sky)

## Repo-Übersicht & Dokumentationsstruktur
- **Dies ist die zentrale Projektbeschreibung.** Alle Inhaltsverweise aus dem Repository-Root zeigen hierher.
- **Changelog:** Laufende Änderungen werden unter [`changelog.md`](changelog.md) geführt.
- **Root-Hinweis:** Der Root-`README.md` verweist nur noch auf diesen Ordner, damit Dokumentation und Änderungsprotokoll gebündelt sind.

## Ziel
Dieses Dokument sammelt die notwendigen Verarbeitungsschritte, um aus einem fertig gestackten FITS-Bild in Siril automatisch ein tiefensensitives, deepsky-optimiertes Ergebnis zu erzeugen. Der Fokus liegt auf linearem Input nach dem Stacking sowie einer robusten Qualitätskontrolle, damit ein Skript Parameter adaptiv anpassen kann.

## Erfüllter Aufgabenstatus (task.md)
- **Kurzfristig 1–5**: CLI/Logging, QC-Kapselung (`stat`/`findstar`/`psf`), lineare Pipeline (Hintergrund, Photocal/Whitebalance, Denoise, optionale Deconvolution), Stretch & Farbe, Exporte + QC-Reports.
- **Mittelfristig 1–4**: Session-Handling (`--sessions`, Manifest), Preset-/Konfig-System (`--preset` für JSON/YAML), Qualitäts-Feedback-Schleife (RMS-Vergleich, automatisches Downscaling bei Regression) sowie Referenz-Hooks (Export-Benennung per FITS-Header/Session, UI-State-Schnappschüsse) aus `REFERENCE_Naztronomy.md`.
- **Langfristig 1–2**: UI-/Frontend-Hooks via `--ui-state-dir` (JSON-Snapshots für Pfad-/QC-Anzeige) und erste automatisierte Tests plus Beispiel-Preset/Session-Dateien zur Reproduktion.

**Statuscheck:** Alle Anforderungen aus `task.md` (kurz-, mittel- und langfristig) sind in den Skriptvarianten umgesetzt; weiterer Anpassungsbedarf entsteht nur bei neuen Requirements oder geänderten QC-/Export-Zielen.

## Grundannahmen
- Eingang: lineares, gestacktes FITS (kein Stretch, bereits kalibriert und registriert).
- Arbeitsumgebung: Siril 1.2+ mit Skript-Unterstützung.
- Zwischenergebnisse werden in separaten Dateien abgelegt, um Vergleiche zu ermöglichen.

## Skriptgrundlage (Kurzfristig 1–5 umgesetzt)
- **Dateien**: `siril_auto_everything.sh` (Bash) und `siril_auto_everything.py` (Python)
- **Aufruf (Bash)**: `./siril_auto_everything.sh -i /pfad/zum/stack.fit -w /tmp/work -o /tmp/out [--skip-deconvolution]`
- **Aufruf (Python)**: `python siril_auto_everything.py -i /pfad/zum/stack.fit -w /tmp/work -o /tmp/out [--skip-deconvolution] [--siril-bin /pfad/zu/siril] [--sessions sessions.json] [--preset preset.yaml] [--ui-state-dir ./ui_state]`
- **Pfadparameter & Logging**:
  - Erwartet Eingabe-/Arbeits-/Output-Ordner als Argumente; legt `logs/` und `metrics/` im Arbeitsordner an.
  - Beide Varianten erzeugen temporäre `.ssf`-Skripte mit `requires 1.2` + `log` und schreiben Siril-Ausgaben in pro-Schritt-Logs.
- **Default-Blueprint**:
  - Ohne `--preset` lädt die Python-Variante automatisch `blueprint_default.json` (abgeleitet aus `REFERENCE_Naztronomy.md`) als Basiskonfiguration für Stretch/Sättigung, Hintergrundordnung und Export-Benennung.
  - Override durch eigene Presets (JSON/YAML) bleibt möglich; fehlende Felder fallen auf die Blueprint- oder Inline-Defaults zurück.
- **Qualitätsmessungen**:
  - Kapselt `stat`, `findstar` und `psf` pro Verarbeitungsstufe; schreibt Kennzahlen nach `metrics/*.json`.
  - Einfache Clip-Detektion (Min <= 0) steuert Hintergrund-Ordnung herunter (4 → 3) bei Black-Clipping-Gefahr.
- **Lineare Verarbeitungskette & Export**:
  1. Hintergrundkorrektur (`bg` mit Masken-Safeguard via `findstar`/`seqmask`).
  2. Photometrische Kalibration mit Fallback `whitebalance` bei Fehlern.
  3. Rauschminderung (`sdenoise`, adaptives Sigma über Hintergrund-RMS), optionale Deconvolution (`psf`-gestützt, abschaltbar).
  4. **Stretch & Farbe**: Autostretch + Asinh, MTF-Finetuning mit Blackpoint aus `stat`-Median/Std; optionale SCNR bei Farbrausch und moderate Sättigung nur bei stabiler SNR.
  5. **Exporte & QC-Reporting**: lineares Ergebnis und gestretchte Ausgaben mit referenzierbaren Namen (Preset-Template, FITS-Header-Tokens), TIFF/PNG-Derivate, QC-JSONs inkl. aggregierter `quality_summary.json`.

### Mittelfristige Ergänzungen (Aufgaben 4–6)
- **Session-Handling**: Über `--sessions` können mehrere gestackte FITS mit eigenen Arbeits-/Output-Unterordnern verarbeitet werden; ein `session_manifest.json` fasst die Ergebnisse zusammen.
- **Preset-/Konfig-System**: `--preset` akzeptiert JSON/YAML-Profile (Asinh/Sättigung, Hintergrundordnung, Drizzle/Feather-Hinweise) und validiert Werte vor dem Lauf.
- **Qualitäts-Feedback-Schleife**: Vergleicht RMS vor/nach Denoise; erkennt Verschlechterung und wiederholt den Schritt mit reduzierter Stärke, um die Qualitätsziele aus `task.md` abzudecken.
- **Referenz-Hooks**: Export-Basisnamen nutzen Preset-Templates (`export_name_template`) und FITS-Header-Tokens (OBJECT, FILTER, DATE-OBS), UI-State-Snapshots liefern Session-/QC-Infos für Frontends.

### Python-Skriptvariante (`siril_auto_everything.py`)
- Entspricht der Bash-Vorlage, bietet aber Python-Logging und Fehlermeldungen über `subprocess.CalledProcessError` mit Log-Pfad.
- CLI-Flags bleiben kompatibel; zusätzlich kann `--siril-bin` für alternative Siril-Pfade gesetzt werden.
- `--ui-state-dir` legt pro Session eine JSON-Zusammenfassung (Input/Output-Pfade, Exportnamen, QC-Ort, Header-Tokens) für Frontends ab.
- Legt dieselben Zwischenablagen (`logs/`, `metrics/`) und Ergebnisdateien an wie das Shell-Skript.

> Hinweis: Die Siril-Kommandos sind als Skript-Templates ausgelegt; Log-Ausgaben dienen der Kennzahlen-Extraktion und lassen sich bei Bedarf weiter parsen.

## Empfohlene Prozessschritte für das Skript
1. **Session-Setup**: Arbeitsverzeichnis setzen (`cd`), Input kopieren/umbenennen, Protokollierung einschalten (`requires 1.2` erlaubt `log`-Ausgabe).
2. **Platten-/Gradienten-Korrektur**: Hintergrundmodell mit `bg` (polynomiell 3–4 Ordnung) oder `bkg` erzeugen; Safeguards gegen Überkorrektur (Masken mit `seqmask`/`findstar`).
3. **Farbbalance und Kalibration**:
   - Photometrische Farbkalibration per `photocal` mit automatischer Sternsuche und Katalog (z. B. APASS).
   - Alternativ: `whitebalance` auf neutralem Hintergrund, falls Photokalibration mangels Sterne scheitert.
4. **PSF- und Sternanalyse**: `findstar` + `psf` ausführen, um FWHM/HFD als Referenz für spätere Qualitätsmessungen zu erhalten.
5. **Deconvolution (optional, maskiert)**: `deconv` mit PSF-Werten aus Schritt 4 und Sternmaske; Abbruch, falls Artefakte (z. B. steigende Ringing-Statistiken) erkannt werden.
6. **Rauschminderung im linearen Bereich**: `sdenoise` oder `nlmeans` (Sigma-guided); Stärke anhand Hintergrund-RMS steuern.
7. **Farbrauschen/Grünstich**: `scnr green` oder `chrominance`-Rauschfilter nur bei messbarem Farbrausch-Überschuss.
8. **Lineares Stretching**:
   - Start mit `autostretch`/`asinh` für weiches Highlight-Preserving Stretch.
   - Feintuning mit `mtf` oder `histogram`-Operationen; Blackpoint aus Hintergrund-Statistiken ableiten.
9. **Sättigung & Farbkontrast**: `saturation` moderat erhöhen, abhängig von SNR; vermeiden, wenn Sterne bereits clippen.
10. **Sternreduktion (optional)**: Morphologischer Filter via Starmaske (`extract_star_mask`, dann `morpho`/`mtf`-basierte Reduktion) zur Kontraststeigerung des Nebels.
11. **Lokalkontrast/Feinstruktur**: `logstretch`/`clahe` (falls verfügbar) in leichter Dosierung; nur anwenden, wenn SNR ausreichend.
12. **Endkontrolle & Export**: `stat` auf Hintergrundregion, `psf`-Vergleich, und Export als 16-bit TIFF/PNG sowie archiviertes FITS mit angewandtem Stretch.

## Qualitätsmetriken für automatisierte Optimierung
- **SNR und Hintergrund-RMS**: `stat` liefert mittleren Hintergrund und RMS; Ziel: RMS nach Rauschminderung senken, ohne Black Clipping (Pixelanzahl bei Wert 0 beobachten).
- **Sternschärfe**: Mittelwert/Median von FWHM oder HFD aus `psf`; Verbesserungen nach Deconvolution erfassen, Verschlechterungen -> Schritt zurückrollen.
- **Sternanzahl und -Rundheit**: `findstar`-Count und ellipticity; starke Elliptizität weist auf Fehlfokus oder Tracking hin -> aggressives Stretch vermeiden.
- **Sättigungsanteil**: Anteil gesättigter Pixel (`stat`-Histogramm); wenn >0.5 % steigt, Sättigungs-/Stretch-Intensität reduzieren.
- **Farbneutralität**: Mittelwerte der RGB-Kanäle im Hintergrund; Abweichung >5 % -> `whitebalance` oder SCNR erneut anwenden.

## Aufgabenliste zur Skripterstellung
- Eingabeverarbeitung und Logik
  - Parameterdatei/Defaults für Pfade, Ziel-Helligkeitswerte und Sicherheitsschwellen (RMS, FWHM, Clip-Limits) definieren.
  - Routine für Zwischenspeicher (z. B. `_bgcorr.fit`, `_denoise.fit`, `_stretch.fit`).
- Automatisierte Messungen
  - Funktionen/Blöcke für `stat`, `findstar`, `psf` implementieren und relevante Kennzahlen als Variablen speichern.
  - Prüfungen auf Clip-Werte und Sättigungsanteil einbauen, um Schritte abzubrechen oder Parameter zu senken.
- Verarbeitungsschritte implementieren
  - Hintergrund/Gradient entfernen (`bg`/`bkg`) mit adaptiver Ordnung je nach Gradientenstärke.
  - Farbkalibration (`photocal` mit Fallback `whitebalance`).
  - Denoise + optional Deconvolution mit Maskensteuerung.
  - Mehrstufiges Stretching (Autostretch → Asinh → MTF/Histogram-Feinjustage).
  - Optionale Sternreduktion und Sättigungsanhebung abhängig von SNR/Clip-Checks.
- Qualitäts-Feedback-Schleife
  - Vor/Nach-Messungen vergleichen (RMS, FWHM, Clip-Anteil) und bei Verschlechterung letzte Aktion rückgängig machen oder Parameter reduzieren.
  - Finalen Qualitätsreport (Textdatei) mit allen Messwerten erzeugen.
- Export
  - Gestretchte Version als 16-bit TIFF/PNG und als finales FITS sichern.
  - Optional Preview-JPG mit kleinerer Auflösung exportieren.

## Referenzskript (Naztronomy)
- **Datei**: `REFERENCE_Naztronomy.md` fasst das Beispiel „Naztronomy - OSC Image Preprocessor“ nach Funktionen und Architektur zusammen (PyQt6-UI, Siril-Integration, Presets, QC-Metriken).
- **Zweck**: Dient als Funktions- und Architektur-Referenz, z. B. für UI-Hooks, Preset-Format und QC-Logik.

## Weiterführende Artefakte
- **task.md**: konkrete Umsetzungsschritte und To-dos für die nächsten Skriptiterationen.
- **examples/**: Beispiel-Preset (`sample_preset.json`) und Session-Definition (`sample_sessions.yaml`) für reproduzierbare Aufrufe.
- **tests/**: Kleine Unittests für Kennzahlen-Parsing, Blackpoint-Ableitung und Export-Benennung (`python -m unittest discover -s Siril_autoEverything/tests`).
