# Changelog

## 2026-02-02 08:02:59 +0000
- Pixelart-Upload-Handler korrigiert (AsyncWebServer ohne `responseSent`), damit der Sketch wieder kompiliert. Quelle: `main.sketch`.

## 2026-02-02 07:51:01 +0000
- Pixelart‑Speicher persistent auf dem ESP32 ergänzt (LittleFS) inklusive `/api/pixelart` zum Speichern/Laden. Quelle: `main.sketch`.
- UI‑Save/Load erweitert: speichert nun Browser + ESP32, lädt bevorzugt vom ESP32. Quelle: `main.sketch`.
- Dokumentation für persistentes Pixelart‑Speichern aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-02-02 07:42:36 +0000
- Schlafzeit über Web‑UI konfigurierbar gemacht und in LittleFS persistent gespeichert (auch nach Stromausfall). Quelle: `main.sketch`.
- Schlafzeit‑API ergänzt (`/api/sleep`) und UI‑Felder für Start/Ende/Dimmung ergänzt. Quelle: `main.sketch`.
- Dokumentation auf UI‑Primärkonfiguration und Persistenz aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-02-02 07:10:59 +0000
- Schlafzeit-Dimmung ergänzt: Schlafmodus erlaubt 0–20 % Helligkeit, inkl. Skalierung der Panel-Helligkeit im Sleep-Window. Quelle: `main.sketch`.
- Dokumentation für `SLEEP_DIM_PERCENT` ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-02-01 14:29:01 +0000
- Zeitzonen-Definition auf CET/CEST umgestellt, damit die NTP-Uhr Winterzeit/Sommerzeit korrekt abbildet. Quelle: `main.sketch`.
- Schlafzeit-Logik ergänzt: zeitgesteuertes Abschalten des Panels mit NTP-Prüfung, wirkt auch nach Neustart. Quelle: `main.sketch`.
- Dokumentation zur Zeitzone und Schlafzeit ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-22 10:25:00 +0000
- Pixelart Save/Load stabilisiert: versioniertes LocalStorage‑Format, validierte Dimensionen und klarere Fehlermeldungen. Quelle: `main.sketch`.
- Buttons explizit als `type="button"` markiert, um Save/Load‑Clicks zuverlässig ohne Seiteneffekte auszuführen. Quelle: `main.sketch`.
- Dokumentation für das robuste Save/Load‑Verhalten aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-21 06:51:15 +0000
- Web‑UI im Teenage‑Engineering‑Stil überarbeitet: helles Kartenlayout, neue Header‑Struktur, Mono‑Typografie und modernisierte Controls/Canvas‑Panel. Quelle: `main.sketch`.
- Dokumentation zur neuen UI‑Designsprache ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-20 12:54:28 +0000
- Uhranzeige stabilisiert (fixe Zeichenposition) und UI‑Regler für Uhrfarbe + Uhr‑Helligkeit ergänzt. Quelle: `main.sketch`.
- Dokumentation für Uhrfarbe/Uhr‑Helligkeit ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-20 11:51:00 +0000
- Wetter‑Layout angepasst: Uhr oben vollflächig, unten links 16×16‑Icon, unten rechts Temperatur. Quelle: `main.sketch`.
- Dokumentation für das neue Wetter‑Layout aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-20 10:13:35 +0000
- Wetteranzeige im Uhr‑Modus auf Icon‑Darstellung umgestellt und Standort‑Label entfernt. Quelle: `main.sketch`.
- Dokumentation für Wetter‑Icons angepasst. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-20 10:07:28 +0000
- Stopuhr‑Kette ergänzt: Bei exakt einer Minute wird der komplette Panel‑Rahmen als Linie dargestellt. Quelle: `main.sketch`.
- Dokumentation für Stopuhr‑Rahmenverhalten ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-20 08:51:35 +0000
- Optionales Wetter‑Overlay für Koblenz im Uhr‑Modus ergänzt (Temperatur + Kurzcode via Open‑Meteo), inkl. UI‑Toggle, WebSocket‑API und Fetch‑Logik im Sketch. Quelle: `main.sketch`.
- Dokumentation für Wetter‑Option, Konfiguration und Bedienung ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-20 07:51:16 +0000
- NTP‑Uhr (HH:MM/HH:MM:SS) und Stopuhr (HH:MM:SS) inkl. LED‑Kette am Rand, Display‑Modi und minimaler Start‑Helligkeit implementiert; Boot‑Text entfernt. Quelle: `main.sketch`.
- Dokumentation für Uhr/Stopuhr‑Bedienung, NTP‑Konfiguration und WebSocket‑API ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-17 10:26:06 +0000
- WLED‑ähnliche Effekte erweitert (Twinkle, Scanner, Waves) inkl. Effect‑State und Render‑Ticks im Sketch sowie UI‑Optionen. Quelle: `main.sketch`.
- Dokumentation der neuen Effekte in README/How‑To/Tutorial sowie Tasks ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`, `tasks.md`.

## 2026-01-17 09:57:45 +0000
- WLED‑ähnliche Effekt‑Engine im Sketch implementiert (Matrix, Blink, Colorfading, Rainbow, Kaminfeuer) inklusive UI‑Parametersteuerung und WebSocket‑API. Quelle: `main.sketch`.
- Dokumentation für Effekt‑Steuerung und neue UI‑Sektion ergänzt (README, How‑To, Tutorial) und Roadmap‑Status aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`, `tasks.md`.

## 2026-01-17 09:46:24 +0000
- Umsetzungs-Task für WLED-ähnliche Animationen ergänzt (Effekt-Engine, Effekte, UI-Parametersteuerung, Akzeptanzkriterien). Quelle: `tasks.md`.
- Taskliste in README/How-To/Tutorial um Umsetzungs-Task für Animationen ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-17 08:21:46 +0000
- GIF-Upload im Browser auf max. 50 Frames limitiert, um anim.bin-Uploads zu begrenzen. Quelle: `main.sketch`.
- Dokumentation zur GIF-Frame-Limitierung ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-17 08:14:01 +0000
- Pixelart Save/Load lokal im Browser (LocalStorage) ergänzt, ohne Änderungen an der Redraw-Logik. Quelle: `main.sketch`.
- Dokumentation für lokalen Save/Load-Workflow ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-17 08:00:32 +0000
- Bild- und Panel-Redraw-Workflow auf anim.bin-Pipeline umgestellt: Browser packt Single-Frame wie GIF, Upload nach LittleFS, ESP32 rendert lokal. Quelle: `main.sketch`.
- Dokumentation für anim.bin-basierte Bild-/Redraw-Übertragung aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-17 07:31:50 +0000
- Panel-Redraw/Panel-Bulk-Jobs robust gemacht: chunked Pixel-Batches, Queue/Lock gegen Unterbrechung und sauberes Nachziehen bei parallelen UI-Aktionen. Quelle: `main.sketch`.
- Dokumentation für robusten Panel-Redraw aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 15:14:43 +0000
- Aufgaben-Backlog als `tasks.md` ergänzt und Querverweise in README/How‑To/Tutorial gesetzt. Quellen: `tasks.md`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 14:50:54 +0000
- Aufgaben zur Umsetzung der Roadmap ergänzt (Pixelart JSON Load/Save, WLED‑ähnliche Animationen inkl. UI/Parameter‑Schritten). Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 14:43:40 +0000
- Roadmap für zukünftige Features ergänzt (Pixelart JSON Load/Save, WLED‑ähnliche Animationen mit Parametern). Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 13:46:41 +0000
- Panel-Redraw als Button umgesetzt (statt Doppelklick), sendet Pixelart per `px` erneut ans Panel. Quelle: `main.sketch`.
- Dokumentation auf Button-Workflow aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 13:31:29 +0000
- Panel-Redraw ergänzt: Pixelart-Canvas kann per Doppelklick vollständig via `px` neu an das Panel gesendet werden. Quelle: `main.sketch`.
- Dokumentation für Panel-Redraw ergänzt. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 12:48:57 +0000
- Bild-Upload nutzt Pixelart-Mechanik (Image → Canvas → 64×32 → `px` Updates) für robuste Projektion. Quelle: `main.sketch`.
- Reinit leert Canvas und Panel über `clear`, damit Pixelart nach Neustart zuverlässig funktioniert. Quelle: `main.sketch`.
- Dokumentation für Bild-Upload/Pixelart-Reinit angepasst. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 12:36:23 +0000
- Bild-Upload Pipeline an GIF-Workflow angeglichen (Image → Canvas → Mapping) für korrektes 64×32-Projizieren. Quelle: `main.sketch`.
- Dokumentation für Bild-Mapping aktualisiert. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 10:50:39 +0000
- GIF-Mapping-Variable umbenannt, um JavaScript-Syntaxfehler zu vermeiden, der das WebSocket-Setup blockieren konnte. Quelle: `main.sketch`.
- Troubleshooting für WebSocket-Status ergänzt (connecting bleibt stehen) in den MD-Dokumenten. Quellen: `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 10:10:01 +0000
- Full-Frame-Upload sendet exakt das Uint8Array-Slice, um abgeschnittene Bildübertragung zu vermeiden. Quelle: `main.sketch`.

## 2026-01-16 10:00:55 +0000
- Farbpalette ergänzt und Canvas auf 64×32 intern fixiert, nur optisch skaliert (korrektes 1:1 Mapping). Quellen: `main.sketch`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 09:47:16 +0000
- OTA-Link aus UI-Header entfernt, passend zur deaktivierten OTA-Funktion. Quelle: `main.sketch`.

## 2026-01-16 09:44:35 +0000
- Canvas-Input korrigiert (Pointer-Events + korrekte Skalierung) und Grid zur Pixeltrennung ergänzt. Quellen: `main.sketch`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 09:19:45 +0000
- Full-Frame-Upload sendet Uint8Array statt ArrayBuffer, um partielle Panel-Updates zu vermeiden. Quelle: `main.sketch`.

## 2026-01-16 09:07:18 +0000
- WebSocket-Variable im UI auf `var` umgestellt, um TDZ-Fehler bei früher Nutzung zu vermeiden. Quelle: `main.sketch`.

## 2026-01-16 08:57:05 +0000
- WebSocket-Init im UI vor Helligkeits-Events verschoben, um JS-ReferenceError zu vermeiden. Quelle: `main.sketch`.

## 2026-01-16 08:34:42 +0000
- OTA entfernt (ElegantOTA inkl. Endpoint), Dokumentation bereinigt und als spätere Erweiterung markiert. Quellen: `main.sketch`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 08:18:21 +0000
- OTA Auth wieder entfernt, um ElegantOTA 3.1.7 Linker-Error zu vermeiden (zurück auf begin ohne Credentials). Quellen: `main.sketch`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 08:14:19 +0000
- OTA Auth ergänzt, damit ElegantOTA 3.1.7 mit Login kompiliert (OTA_USER/OTA_PASS, begin mit Credentials). Quellen: `main.sketch`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 07:49:10 +0000
- Helligkeitssteuerung im Sketch ergänzt (UI‑Regler, WebSocket `bright`, `setBrightness8`). Quellen: `main.sketch`, `README.md`, `HOWTO.md`, `TUTORIAL.md`.

## 2026-01-16 07:46:26 +0000
- Taskliste in README, Tutorial und How‑To angepasst (CDN‑GIF‑Lib bleibt, Multi‑Panel verschoben; Fokus auf Helligkeit, Presets, Animation‑Builder). Quellen: `README.md`, `TUTORIAL.md`, `HOWTO.md`.

## 2026-01-16 07:42:08 +0000
- Taskliste mit nächsten notwendigen Aufgaben in README, Tutorial und How‑To ergänzt (GIF‑Library lokal, Helligkeit, Presets, Multi‑Panel, Animation‑Builder). Quellen: `README.md`, `TUTORIAL.md`, `HOWTO.md`.

## 2026-01-16 07:37:49 +0000
- Implementierungscheck ergänzt (HUB75, Pixelart, Bild‑Upload, GIF‑Import, OTA) und in README/Tutorial/How‑To verlinkt. Quelle: `main.sketch`.

## 2026-01-16 07:32:25 +0000
- README erweitert um Überblick, PRD, Systemarchitektur, Hardware‑Setup, Display‑Engine, OTA/Netzwerk, Performance, Einschränkungen und Zusammenfassung; Inhalte aus `main.sketch` abgeleitet. Quelle: `main.sketch`.
- Tutorial ergänzt um Überblick und Hardware‑Setup‑Schritt. Quelle: `main.sketch`.
- How‑To ergänzt um Überblick und OTA‑How‑To. Quelle: `main.sketch`.

## 2026-01-16 07:25:42 +0000
- Dokumentation reengineered aus `main.sketch` und als `README.md` zusammengeführt (Features, API, Animationsformat, Troubleshooting). Quelle: `main.sketch`.
- Tutorial ergänzt (`TUTORIAL.md`) für Konfiguration, Flash und UI‑Bedienung. Quelle: `main.sketch`.
- How‑To ergänzt (`HOWTO.md`) für Reinit, WebSocket‑Frames und Animationen. Quelle: `main.sketch`.
