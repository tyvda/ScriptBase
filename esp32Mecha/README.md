# ESP32 Mechanik-Controller (esp32Mecha)

Firmware-Projekt für einen ESP32 DevKit V1 als Slave-Controller für kinetische Mechanik mit:
- 2x Stepper über TMC2209 (Step/Dir, Standalone)
- 4x SG90 Servos
- Web-UI zum Vertesten der Mechanikelemente
- JSON-API für externe Steuerung
- OTA-Updates via WLAN

## Projektziel

Dieses Unterprojekt setzt das Lastenheft „Firmware für ESP32 Mechanik-Controller" um: non-blocking Motion-Control, damit während laufender Bewegungen weiterhin Netzwerkbefehle verarbeitet werden können.

## Hardware / Pinout (fix)

### Stepper (TMC2209, Step/Dir)
- Motor 1: `STEP=GPIO18`, `DIR=GPIO19`
- Motor 2: `STEP=GPIO21`, `DIR=GPIO22`

### Servos (SG90, 5V)
- Servo 1: `GPIO23`
- Servo 2: `GPIO25`
- Servo 3: `GPIO26`
- Servo 4: `GPIO27`

### Netzwerk
- Modus: WLAN Station (STA)
- IP: DHCP

## Firmware-Funktionen

- **Non-blocking Stepper-Steuerung** mit `AccelStepper` (`run()` im `loop()`, keine delay-basierte Bewegungslogik).
- **Stepper-Features**: absolute/relative Ziele, Geschwindigkeit, Beschleunigung.
- **Servo-Steuerung** mit `ESP32Servo` (0..180°), inkl. optionalem sanften Nachfahren (1°-Schritte zeitbasiert).
- **Webserver + Web-UI** für Testbetrieb direkt im Browser.
- **JSON-API** unter `POST /api/control`.
- **OTA** via `ArduinoOTA`.
- **WLAN-Reconnect** ohne Motor-Neuinitialisierung (keine „wilden Zuckungen").

## API

### `POST /api/control`

Beispiel Stepper absolut:

```json
{
  "stepper": {
    "id": 1,
    "mode": "absolute",
    "target": 5000,
    "speed": 1400,
    "accel": 700
  }
}
```

Beispiel Stepper relativ:

```json
{
  "stepper": {
    "id": 2,
    "mode": "relative",
    "target": -200,
    "speed": 1200,
    "accel": 600
  }
}
```

Beispiel Servo:

```json
{
  "servo": {
    "id": 3,
    "angle": 135
  }
}
```

Kombiniert (ein Request):

```json
{
  "stepper": { "id": 1, "mode": "relative", "target": 100, "speed": 1000, "accel": 500 },
  "servo": { "id": 1, "angle": 45 }
}
```

### `GET /api/health`
Liefert WLAN-Status, IP, aktuelle Stepper-Positionen sowie Servo Current/Target.

## TMC2209 Hinweis (StealthChop)

In dieser Umsetzung läuft der TMC2209 im **Standalone Step/Dir**-Modus. Ohne UART-Anbindung können Register nicht per Firmware gesetzt werden. StealthChop muss daher über die Treiber-Hardware-Konfiguration (CFG/MS Pins / Modul-Defaults) aktiv sein.

## Abhängigkeiten

- `WiFi.h`
- `WebServer.h`
- `ArduinoJson`
- `ArduinoOTA`
- `AccelStepper`
- `ESP32Servo`

## Schnellstart

1. In `main.sketch` WLAN-Zugangsdaten setzen (`WIFI_SSID`, `WIFI_PASS`).
2. Sketch auf ESP32 DevKit V1 flashen.
3. Serielle Konsole öffnen und DHCP-IP notieren.
4. Browser öffnen: `http://<ESP32-IP>/`.
5. Mechanik über UI und/oder JSON-API testen.

## Dokumente

- [HOWTO.md](HOWTO.md) – Kurzrezepte für typische Aufgaben
- [TUTORIAL.md](TUTORIAL.md) – Schritt-für-Schritt Inbetriebnahme
- [tasks.md](tasks.md) – Backlog / nächste Ausbaustufen
- [changelog.md](changelog.md) – Änderungsprotokoll
