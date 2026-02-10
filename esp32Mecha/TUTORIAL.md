# Tutorial – esp32Mecha Inbetriebnahme

## 1) Ziel
Du nimmst den ESP32 Mechanik-Controller in Betrieb und testest 2 Stepper + 4 Servos über Browser-UI und JSON-API.

## 2) Voraussetzungen
- ESP32 DevKit V1
- 2x TMC2209 (Step/Dir verdrahtet)
- 4x SG90
- 5V-Versorgung für Servos (gemeinsame Masse mit ESP32)
- Arduino IDE oder PlatformIO

## 3) Pinout validieren
- Stepper1: `18/19`
- Stepper2: `21/22`
- Servo1..4: `23/25/26/27`

Wenn anders verdrahtet, muss die Hardware angepasst werden, da das Lastenheft diese Pins fix vorgibt.

## 4) Firmware konfigurieren
In `main.sketch`:
- `WIFI_SSID`
- `WIFI_PASS`
- optional `HOSTNAME`

## 5) Flashen
- Board: ESP32 Dev Module
- Port: USB
- Sketch hochladen
- Serielle Ausgabe lesen (`115200`)

## 6) Web-UI testen
- Browser auf `http://<ESP32-IP>/`
- Stepper 1/2 target/speed/accel setzen
- Servos über Slider bewegen

## 7) API testen
Mit `curl` Befehle aus `HOWTO.md` senden.

## 8) Non-blocking Verhalten verifizieren
- Einen längeren Stepper-Move starten (z. B. target 10000)
- Währenddessen wiederholt Servo-Befehle senden
- Erwartung: API bleibt reaktionsfähig, da `run()` pro Loop aufgerufen wird und keine delay()-Bewegungsschleifen existieren.

## 9) OTA testen
- Nach erfolgreicher WLAN-Verbindung OTA-Port in der IDE wählen
- Geänderten Sketch OTA hochladen

## 10) TMC2209 / StealthChop
- Firmware nutzt Step/Dir Standardlogik.
- StealthChop muss im Standalone-Betrieb über Treiber-Konfiguration aktiv sein.
