# Changelog

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
