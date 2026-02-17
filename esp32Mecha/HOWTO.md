# HOWTO – esp32Mecha

## WLAN konfigurieren
1. `main.sketch` öffnen.
2. `WIFI_SSID` und `WIFI_PASS` eintragen.
3. Neu flashen.

## Stepper bewegen (absolute Position)
```bash
curl -X POST http://<ESP32-IP>/api/control \
  -H 'Content-Type: application/json' \
  -d '{"stepper":{"id":1,"mode":"absolute","target":3000,"speed":1200,"accel":600}}'
```

## Stepper bewegen (relative Position)
```bash
curl -X POST http://<ESP32-IP>/api/control \
  -H 'Content-Type: application/json' \
  -d '{"stepper":{"id":2,"mode":"relative","target":-250,"speed":1000,"accel":500}}'
```

## Servo setzen
```bash
curl -X POST http://<ESP32-IP>/api/control \
  -H 'Content-Type: application/json' \
  -d '{"servo":{"id":4,"angle":90}}'
```

## Zustand prüfen
```bash
curl http://<ESP32-IP>/api/health
```

## OTA nutzen
1. ESP32 muss im gleichen Netz erreichbar sein.
2. Arduino IDE → Netzwerk-Port des ESP32 auswählen.
3. Sketch hochladen (OTA).

## WLAN-Ausfall-Verhalten
- Firmware versucht periodisch Reconnect.
- Stepper-/Servo-Objekte bleiben aktiv, es erfolgt keine harte Neuinitialisierung in der Reconnect-Schleife.
