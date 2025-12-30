# Siril Auto-Everything (Deep-Sky)

## Ziel
Dieses Dokument sammelt die notwendigen Verarbeitungsschritte, um aus einem fertig gestackten FITS-Bild in Siril automatisch ein tiefensensitives, deepsky-optimiertes Ergebnis zu erzeugen. Der Fokus liegt auf linearem Input nach dem Stacking sowie einer robusten Qualitätskontrolle, damit ein Skript Parameter adaptiv anpassen kann.

## Grundannahmen
- Eingang: lineares, gestacktes FITS (kein Stretch, bereits kalibriert und registriert).
- Arbeitsumgebung: Siril 1.2+ mit Skript-Unterstützung.
- Zwischenergebnisse werden in separaten Dateien abgelegt, um Vergleiche zu ermöglichen.

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
