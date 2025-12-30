# Aufgaben zur Umsetzung des Siril-Auto-Everything-Skripts

## Kurzfristig
1. **CLI-/Skriptgrundlage bauen**
   - Skriptgerüst in Bash/Siril erstellen, das ein gestacktes FITS als Input annimmt und einen Arbeitsordner vorbereitet.
   - Logging aktivieren (`requires 1.2`, `log`) und saubere Pfadparameter (Input, Arbeits- und Output-Ordner) definieren.
2. **Qualitätsmessungen kapseln**
   - Funktionen für `stat`, `findstar` und `psf` erstellen; Ergebnisse als Variablen/JSON abspeichern.
   - Prüfungen auf Black-Clipping und Sättigung implementieren, um bei Überschreitung Schwellenwerte zu senken oder Schritte zu überspringen.
3. **Lineare Verarbeitungskette**
   - Hintergrundkorrektur (`bg`/`bkg`) mit adaptiver Ordnung (3–4) und Masken-Safeguard (`seqmask`/`findstar`).
   - Photokalibration (`photocal`) mit Fallback `whitebalance`.
   - Rauschminderung (`sdenoise`/`nlmeans`) gesteuert durch Hintergrund-RMS.
   - Optional: Deconvolution mit PSF-Parametern und Abbruchkriterium bei Ringing.
4. **Stretch & Farbe**
   - Autostretch/Asinh als Start, Feintuning via `mtf` oder Histogramm; Blackpoint aus Hintergrund-Statistiken ableiten.
   - Sättigung moderat anheben nur bei stabiler SNR; SCNR/Chrominance gegen Farbrauschen bei Bedarf.
5. **Exports & Berichte**
   - Gestretchte Ausgabe als TIFF/PNG sowie archiviertes FITS erzeugen.
   - Zusammenfassung der QC-Metriken (RMS, FWHM, Clipping, Farbdrift) als Text/JSON ablegen.

## Mittelfristig
1. **Stapel- und Session-Handling**
   - Mehrere Sessions unterstützen (Lights/Darks/Flats/Biases), Kopieren/Symlink in Arbeitsordner, optional separate Stacks.
   - Merge-Pfad für Multi-Session-Stapel mit optionaler Feathering-Option.
2. **Preset-/Konfig-System**
   - JSON- oder YAML-basierte Presets für Parameter (Drizzle, Feather, Filter-σ, Stretch-Profile) implementieren.
   - Validierung der Preset-Werte und Fallbacks bei fehlenden Feldern.
3. **Qualitäts-Feedback-Schleife automatisieren**
   - Vor/Nach-Messungen vergleichen; bei Verschlechterung der Kennzahlen automatische Parameterabsenkung oder Schritt-Wiederholung.
   - Optionale Black-Frame-Erkennung und Ausschluss vor dem Stack.
4. **Integration von Referenzideen**
   - Hooks für UI-/Preset-Mechaniken aus `REFERENCE_Naztronomy.md` adaptieren (z. B. Session-Listen, Export-Benennung aus FITS-Headern).

## Langfristig
1. **UI/Frontend-Anbindung**
   - Leichte Web- oder Desktop-UI an das Skript koppeln (nur Hooks, kein eigenständiges HTML im Repo), um Pfade, Presets und QC-Reports anzuzeigen.
2. **Automatisierte Tests & Beispiel-Datenpfad**
   - Tests für Kennzahl-Extraktion und Parameter-Downscaling bereitstellen.
   - Beispiel-Konfigurationen und Dummy-FITS für End-to-End-Durchläufe hinzufügen.
