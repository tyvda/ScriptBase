2026-01-16 17:05:43 UTC
- esp32Hub75 task.md um "Nächste Aufgaben" ergänzt und Doku-Verweise aktualisiert.

2026-01-16 14:34:43 UTC
- esp32Hub75 Preview-Redraw als Line-Scanning umgesetzt und Doku-Hinweise angepasst.

2026-01-16 14:03:32 UTC
- esp32Hub75 Preview-Redraw robuster gemacht (Offscreen-Buffer + requestAnimationFrame) und Doku-Hinweise ergänzt.

2026-01-16 12:48:44 UTC
- esp32Hub75 task.md ergänzt und in README, HOWTO sowie TUTORIAL referenziert (Umsetzungsschritte für geplante Features).

2026-01-16 12:41:36 UTC
- esp32Hub75-Dokumentation erweitert: geplante Features (Pixelart JSON Load/Save; WLED-ähnliche Animationen mit Parametern) in README, HOWTO und TUTORIAL ergänzt.

2025-12-30 15:21:31 UTC
- Blueprint-Default `Siril_autoEverything/blueprint_default.json` aus der Naztronomy-Referenz hinterlegt; Python-Pipeline lädt es automatisch, wenn kein eigenes Preset angegeben ist.
- `Siril_autoEverything/siril_auto_everything.py` um Blueprint-Erkennung erweitert und Tests (`Siril_autoEverything/tests/test_metrics.py`) hinzugefügt, die den Default-Load verifizieren.
- README.md (Root & Siril_autoEverything) mit Hinweis auf das Standard-Blueprint ergänzt.

2025-12-30 13:19:55 UTC
- README.md und Siril_autoEverything/README.md ergänzt um Statuscheck, dass alle in task.md definierten Anforderungen umgesetzt s
ind und nur neue Vorgaben weitere Arbeiten erfordern.
- Siril_autoEverything/task.md mit Statuscheck versehen, der den abgeschlossenen Aufgabenstand festhält.

2025-12-30 11:31:30 UTC
- `siril_auto_everything.py` erweitert um Export-Benennung per Preset/FITS-Header, UI-State-Hooks (`--ui-state-dir`) und Manifest-Updates für Referenz-/Frontend-Anbindung.
- Neue Artefakte: Beispiel-Preset/Session-Dateien unter `Siril_autoEverything/examples/`, Unittests (`Siril_autoEverything/tests/`) für Kennzahlen-Parsing/Exportnamen, Paket-Init zur Importfähigkeit.
- Dokumentation (README.md, Siril_autoEverything/README.md, task.md) aktualisiert mit erfüllten Aufgaben 4–6, neuen Hooks und Test-/Beispielhinweisen.

2025-12-30 09:36:54 UTC
- Added Siril_autoEverything/README.md mit Prozess- und Qualitätsleitfaden für ein automatisiertes Siril-Deepsky-Skript ab gestacktem FITS.
- Aktualisierte README.md mit Verweis auf das neue Siril_autoEverything-Projekt und dessen Inhalte.
2025-12-30 09:44:13 UTC
- Hinzugefügt: `Siril_autoEverything/ui.html` als UI-Prototyp für Pfadzuordnung, Preview und Editiersteuerung des Siril-Skripts.
- README-Dateien aktualisiert (Root & Siril_autoEverything) mit Hinweisen zur UI und Nutzung.
2025-12-30 09:55:00 UTC
- Added `Siril_autoEverything/REFERENCE_Naztronomy.md` als Zusammenfassung des GPL-Referenzskripts „Naztronomy - OSC Image Preprocessor“ für UI-/Skriptplanung.
- Aktualisierte README-Dateien mit Hinweisen auf die Referenz und Lizenz-Checkpunkte.
2025-12-30 10:02:17 UTC
- Überarbeitet `Siril_autoEverything/REFERENCE_Naztronomy.md`, um nur funktions- und architekturbezogene Inhalte ohne Lizenz-/Autorangaben zu behalten.
- README-Dateien (Root & Siril_autoEverything) angepasst, damit die Referenz explizit als Funktions-/Architekturvorlage beschrieben wird.
2025-12-30 10:17:37 UTC
- Entfernt: `Siril_autoEverything/ui.html`, UI-Prototyp aus dem Repo genommen.
- Neu: `Siril_autoEverything/task.md` mit kurzfristigen/mittelfristigen/langfristigen Aufgaben zur Skriptumsetzung.
- README-Dateien (Root & Siril_autoEverything) angepasst, um die Aufgabenbasis hervorzuheben und UI-Referenzen zu entfernen.
2025-12-30 10:28:54 UTC
- Neue Skriptbasis `Siril_autoEverything/siril_auto_everything.sh` mit Siril-Templating, Logging, QC-Funktionen (`stat`, `findstar`, `psf`) und linearer Pipeline (Hintergrund, Photocal/Whitebalance, Denoise, optionale Deconvolution).
- `Siril_autoEverything/README.md` um Aufruf, Pipeline und Messlogik für die kurzfristigen Aufgaben 1–3 ergänzt.
- Root-`README.md` aktualisiert: Hinweis auf startfähiges Skript und Fortschritt der kurzfristigen Aufgaben.
2025-12-30 11:04:46 UTC
- siril_auto_everything.py erweitert: Multi-Session-Handling (`--sessions`), Preset-Validierung (JSON/YAML) für Pipeline-Parameter und Qualitäts-Feedback-Schleife für Denoise gemäß task.md (mittelfristige Aufgaben 4–6).
- README.md (Root & Siril_autoEverything) aktualisiert: dokumentiert erfüllte Aufgaben und neue Optionen/Manifest-Exports; verweist auf abgedeckte Requirements.

2025-12-30 11:01:22 UTC
- `siril_auto_everything.py` um Stretch/Farbanpassung (Autostretch + Asinh/MTF, SCNR, Sättigung) erweitert, Exporte für gestretchte Formate (FIT/PNG/TIFF) ergänzt und QC-Gesamtreport (`quality_summary.json`) hinzugefügt.
- README-Dateien (Root & Siril_autoEverything) auf Aufgabenstand 1–5 und neue Export-/Stretch-Funktionen aktualisiert.

2025-12-30 10:34:09 UTC
- Neu: `Siril_autoEverything/siril_auto_everything.py` als Python-Pendant zum Bash-Skript mit identischer Pipeline, Logging/Metric-Erzeugung und Siril-Skript-Templating.
- `Siril_autoEverything/README.md` erweitert um Aufruf- und Feature-Beschreibung der Python-Variante.
- Root-`README.md` angepasst, um beide lauffähigen Skriptvarianten (Bash & Python) zu nennen.
2025-12-30 11:24:20 UTC
- Aktualisiert `Siril_autoEverything/task.md` mit Statusangaben zu erfüllten und offenen Aufgaben inkl. Verweisen auf Skriptumsetzung.
- README.md (Root & Siril_autoEverything) angepasst, um den Aufgabenfortschritt konsistent mit task.md zu dokumentieren.
