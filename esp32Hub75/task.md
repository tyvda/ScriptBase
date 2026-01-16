# Task-Liste: Zukünftige Features (esp32Hub75)

Diese Tasks beschreiben die geplanten Features für den Pixelart‑Editor (JSON Load/Save) sowie WLED‑ähnliche Animationen. Die Umsetzungsschritte sind so strukturiert, dass die Änderungen nachvollziehbar in Code, UI und Dokumentation abgebildet werden können.

## Status (umgesetzt)

- **Pixelart JSON Load/Save**: Client‑seitiger Import/Export inkl. UI‑Buttons und Full‑Frame‑Upload.
- **WLED‑ähnliche Effekte**: Matrix‑Kinofilm, Blink, Colorfading, Rainbow, Kaminfeuer inkl. Parametern und WS‑Steuerung.

## Nächste Aufgaben (Priorität)

1. **Parameter‑Feintuning**: sinnvolle Default‑Werte & Grenzwerte je Effekt validieren.
2. **Preset‑Speicherung**: UI‑Presets für Effekte (lokal im Browser).
3. **Performance‑Profiling**: FPS & CPU‑Last pro Effekt dokumentieren.
4. **UX‑Verbesserungen**: Kontext‑Hinweise je Effekt (welche Parameter wirken).

## A) Pixelart‑Editor: JSON Load/Save (Client‑seitig)

1. **Datenmodell definieren**
   - JSON‑Schema für Canvas‑State (Breite, Höhe, Farbpalette, Pixel‑Matrix/Flat‑Array, optional Brush‑Settings).
2. **Export‑Funktion in der Web‑UI**
   - Aktuellen Canvas‑State in JSON serialisieren.
   - Download als Datei (`.json`) über Client‑seitigen Download triggern.
3. **Import‑Funktion in der Web‑UI**
   - File‑Picker für JSON implementieren.
   - Validierung des Schemas + Größenprüfung (64×32).
   - Canvas aus JSON rekonstruieren und per WebSocket ans Panel senden.
4. **UX & Fehlerhandling**
   - Nutzerfeedback bei ungültigen Dateien/Abmessungen.
   - Optional: Auto‑Clear vor Import.
5. **Dokumentation aktualisieren**
   - README/How‑To/Tutorial um Import/Export‑Flow ergänzen.
6. **Changelog pflegen**
   - Eintrag mit Quelle und Zweck der Änderungen.

## B) Animationen wie WLED (mit Parametern)

1. **Animations‑Framework definieren**
   - API‑Konzept (JSON‑Message `{"t":"fx","name":"matrix","params":{...}}`).
   - Parameter‑Defaults und erlaubte Werte.
2. **Matrix‑Kinofilm**
   - Parameter: Fallgeschwindigkeit, Dichte, Zeichen‑Set, Farbmodus.
3. **Blink**
   - Parameter: Frequenz, Duty‑Cycle, Farben (On/Off), Random‑Seed.
4. **Colorfading**
   - Parameter: Geschwindigkeit, Farbpalette, Übergangs‑Kurve.
5. **Rainbow**
   - Parameter: Scroll‑Speed, Sättigung, Helligkeit, Richtung.
6. **Kaminfeuer**
   - Parameter: Intensität, Flacker‑Rate, Wärme‑Gradient, Noise‑Seed.
7. **UI‑Integration**
   - Presets & Sliders in der Web‑UI.
   - Live‑Preview und Start/Stop Controls.
8. **ESP32‑Runtime**
   - Animation‑Loop + Framebuffer‑Updates.
   - CPU/RAM‑Budget prüfen (DMA‑Stabilität).
9. **Dokumentation & Hinweis zu Parametern**
   - README/How‑To/Tutorial um Animations‑Parameter erweitern.
10. **Changelog pflegen**
   - Eintrag mit Quelle und Zweck der Änderungen.
