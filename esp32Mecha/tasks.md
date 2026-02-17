# Tasks – esp32Mecha

## Must-Have (Lastenheft)
- [x] Fixes Pinout für 2 Stepper + 4 Servos implementiert.
- [x] Non-blocking Stepper-Loop (`AccelStepper::run`) umgesetzt.
- [x] JSON API `POST /api/control` umgesetzt.
- [x] Browser-UI für Vertestung von Mechanikelementen umgesetzt.
- [x] WLAN STA + DHCP umgesetzt.
- [x] OTA via ArduinoOTA integriert.
- [x] WLAN-Reconnect implementiert.

## Nächste Schritte
- [ ] Endstopp-/Homing-Konzept ergänzen.
- [ ] Optional UART-Anbindung der TMC2209 für Laufzeit-Registerkonfiguration (echtes Firmware-Enable von StealthChop, RMS Current, StallGuard etc.).
- [ ] API-Auth (Token / Basic Auth) ergänzen.
- [ ] Preset-System für Bewegungsabläufe (Sequenzen) ergänzen.
- [ ] UI um Live-Positionsanzeige mit Polling erweitern.
