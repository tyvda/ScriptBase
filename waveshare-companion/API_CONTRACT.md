# Waveshare Local AI Companion – Backend-/Frontend-Vertrag v0.1

**Stand:** 2026-11-10  
**Implementierung:** `server/app.py` und `server/pipeline.py` im Companion-MVP.  
**Status:** Dokumentation des **tatsächlich implementierten** MVP, keine Wunsch-API.

## 1. Überblick

Das Waveshare ESP32-S3-Touch-AMOLED-2.16 ist der **Audio-Client**. Das lokale
Ubuntu-Backend übernimmt Spracherkennung (faster-whisper), Textantwort (Ollama)
und Sprachsynthese (Piper). Die Antwort wird **asynchron** bereitgestellt:

1. Client nimmt Audio auf und lädt eine WAV-Datei hoch.
2. Backend gibt sofort eine UUID (`turn_id`) zurück.
3. Client fragt regelmäßig den Zustand ab.
4. Bei `ready` lädt der Client die Antwort-WAV und spielt sie über ES8311 ab.

Basisadresse (Beispiel): `http://192.168.1.123:8000`. Die tatsächliche LAN-IP
des Ubuntu-Rechners einsetzen. **Vom ESP32 aus ist `localhost` falsch.**

## 2. Authentifizierung und Transport

Alle `/api/*`-Endpunkte benötigen:

```http
Authorization: Bearer <COMPANION_TOKEN>
```

- `COMPANION_TOKEN` stammt aus `server/.env.companion` und muss im Client identisch
  konfiguriert werden. Nicht in URLs, Logs oder Git committen.
- `/health`, `/docs` und `/openapi.json` sind bei der aktuellen FastAPI-Instanz
  ohne diesen Bearer-Check erreichbar.
- Der MVP verwendet **HTTP innerhalb eines vertrauenswürdigen LANs**. Token und
  Audiodaten sind dabei nicht transportverschlüsselt. Keine Portweiterleitung
  ins Internet; für Produktion TLS/Pairing ergänzen.
- Das aktuelle Backend enthält **keine CORS-Middleware**. Native ESP32-/LVGL-
  Clients funktionieren per HTTP; ein Browser-Frontend auf einer anderen Origin
  braucht eine angepasste CORS-Konfiguration oder einen Same-Origin-Proxy.

## 3. Verbindliches Audioformat

| Eigenschaft | Upload vom ESP32 | Antwort an ESP32 |
| --- | --- | --- |
| Container | WAV (RIFF/WAVE) | WAV (RIFF/WAVE) |
| Codec | Linear PCM, unkomprimiert | Linear PCM, unkomprimiert |
| Sample Rate | **16.000 Hz** | **16.000 Hz** |
| Bit-Tiefe | **16 Bit** | **16 Bit** |
| Kanäle | **1 (Mono)** | **1 (Mono)** |
| Byte-Reihenfolge | Little Endian | Little Endian |
| HTTP Content-Type | `audio/wav` | `audio/wav` |
| Begrenzung | max. **20 s**, ca. 640.044 Bytes inkl. 44-Byte-Header | Länge variabel |

Die aktuelle ESP32-Firmware nimmt höchstens **12 Sekunden** pro Tastendruck
auf und übernimmt zunächst den **ersten I²S-Eingangsslot** als Monospur. Für die Wiedergabe dupliziert
sie die Mono-Samples in zwei I²S-Slots. Die Slotzuordnung ist auf realer
Hardware noch zu validieren.

**Wichtig:** Der Upload-Body enthält **nur die binären WAV-Bytes** – kein JSON,
kein Base64 und kein `multipart/form-data`.

## 4. HTTP-Endpunkte

| Methode | Pfad | Body / Header | Erfolgsantwort |
| --- | --- | --- | --- |
| `GET` | `/health` | keine Authentifizierung | `200` JSON `{"ok":true}` |
| `POST` | `/api/turns` | `audio/wav`, Bearer, roher WAV-Body | `202` JSON mit `id`, `state` |
| `POST` | `/api/turns?plain=1` | wie oben | `202` `text/plain` mit UUID |
| `GET` | `/api/turns/{id}` | Bearer | `200` JSON mit vollständigem Job-Status |
| `GET` | `/api/turns/{id}/state` | Bearer | `200` `text/plain` mit Zustandswort |
| `GET` | `/api/turns/{id}/audio.wav` | Bearer; erst bei `ready` | `200` `audio/wav` |

### 4.1 Aufnahme hochladen

```http
POST /api/turns HTTP/1.1
Host: 192.168.1.123:8000
Authorization: Bearer <COMPANION_TOKEN>
Content-Type: audio/wav
Content-Length: 320044

<binäre WAV-Bytes, 10 s>
```

Erfolgsantwort (`202 Accepted`, `application/json`):

```json
{
  "id": "e7eb1c04-2171-48ab-8aeb-5665af66b1c4",
  "state": "queued"
}
```

Das `id`-Feld ist die **Job-ID**, keine Gesprächs-/Session-ID. Der erste Status
der Upload-Antwort ist immer `queued`; der Worker kann inzwischen bereits
weiter sein. Bei `?plain=1` kommt stattdessen ausschließlich die UUID als
`text/plain` zurück. Das ist für Mikrocontroller ohne JSON-Bibliothek gedacht.

### 4.2 Status abfragen

```http
GET /api/turns/e7eb1c04-2171-48ab-8aeb-5665af66b1c4 HTTP/1.1
Authorization: Bearer <COMPANION_TOKEN>
```

Antwortbeispiel (`200 OK`, `application/json`):

```json
{
  "id": "e7eb1c04-2171-48ab-8aeb-5665af66b1c4",
  "state": "ready",
  "transcript": "Wie wird morgen das Wetter?",
  "answer": "Das kann ich dir sagen, wenn du mir deinen Ort nennst.",
  "error": "",
  "created_at": "2026-11-10T10:30:00.000000+00:00"
}
```

Alle Felder sind vorhanden. `transcript` und `answer` sind anfangs leere
Strings. Bei `failed` steht in `error` eine Fehlermeldung (max. 300 Zeichen).
`created_at` ist ein ISO-8601-Zeitstempel in UTC.

Kompakte Alternative:

```http
GET /api/turns/e7eb1c04-2171-48ab-8aeb-5665af66b1c4/state HTTP/1.1
Authorization: Bearer <COMPANION_TOKEN>
```

Antwort-Body: `queued`, `transcribing`, `thinking`, `speaking`, `ready` oder
`failed` als reiner Text. **Keine Anführungszeichen, kein JSON.**

### 4.3 Audioantwort herunterladen

```http
GET /api/turns/e7eb1c04-2171-48ab-8aeb-5665af66b1c4/audio.wav HTTP/1.1
Authorization: Bearer <COMPANION_TOKEN>
```

- Bei `ready`: `200 OK`, `Content-Type: audio/wav`, WAV-Datei im Body.
- Vor `ready`: `409 Conflict`, JSON-Fehler `{"detail":"Audio not ready"}`.
- Für unbekannte IDs: `404 Not Found`.
- Der Client muss die WAV-Wiedergabe selbst starten. `ready` ist **kein**
  automatischer Wiedergabebefehl.

## 5. Zustände und UI-Mapping

| Backend-Status | Bedeutung | Empfohlene UI |
| --- | --- | --- |
| `queued` | Upload akzeptiert, Job wartet auf Worker | „In Warteschlange …“ |
| `transcribing` | Whisper erkennt Sprache | „Ich verstehe …“ |
| `thinking` | Ollama generiert Antworttext | „Ich denke nach …“ |
| `speaking` | Piper erzeugt die Antwort-WAV | „Ich formuliere meine Antwort …“ |
| `ready` | WAV liegt zum Download bereit | herunterladen → abspielen |
| `failed` | Verarbeitung fehlgeschlagen | Fehler zeigen, neue Aufnahme anbieten |

Der Client benötigt **zusätzliche lokale Zustände**, die nicht vom Backend
kommen: `idle`, `recording`, `uploading`, `downloading`, `playing`, `offline`.

Empfohlene Client-Sequenz:

```mermaid
stateDiagram-v2
    [*] --> idle
    idle --> recording: Taste drücken
    recording --> uploading: Taste loslassen
    uploading --> queued: HTTP 202
    queued --> transcribing
    transcribing --> thinking
    thinking --> speaking
    speaking --> ready
    ready --> playing: WAV herunterladen
    playing --> idle
    uploading --> offline: Netzwerkfehler
    queued --> failed: Jobfehler
    transcribing --> failed: Jobfehler
    thinking --> failed: Jobfehler
    speaking --> failed: Jobfehler
    failed --> idle: Erneut versuchen
    offline --> idle: WLAN wiederhergestellt
```

Für das MVP nach dem Upload alle **1–2 Sekunden** pollend `GET /api/turns/{id}`
oder `/state` aufrufen; bei `ready` genau einmal die WAV laden. Auf dem Gerät
einen Timeout (z. B. 180 Sekunden) und einen Abbruch für den UI-Dialog
vorsehen. Das ist zunächst nur ein **clientseitiger** Abbruch: Es gibt noch
keinen Backend-Endpoint zum Abbrechen eines Jobs.

## 6. Fehlerbehandlung

| HTTP-Code | Wann? | Client-Reaktion |
| --- | --- | --- |
| `202` | Aufnahme angenommen | ID speichern, Polling starten |
| `401` | Token fehlt oder ist falsch | Konfiguration prüfen, kein endloses Retry |
| `503` | `COMPANION_TOKEN` am Server fehlt | Server-Konfiguration reparieren |
| `413` | WAV-Body zu groß | Aufnahme kürzen (max. 20 s) |
| `415` | `Content-Type` ist nicht `audio/wav` | Header korrigieren |
| `422` | WAV beschädigt oder falsches PCM-Format | Aufnahmeformat korrigieren |
| `404` | Unbekannte Job-ID | neuen Turn beginnen (z. B. nach Serverneustart) |
| `409` | WAV vor `ready` angefordert | weiter auf `ready` warten |
| Netzwerkfehler/Timeout | Server/WLAN nicht erreichbar | UI `offline`, Retry mit Begrenzung |

Ausführungsfehler von Whisper/Ollama/Piper werden normalerweise **nicht** als
HTTP 500 beim Upload zurückgegeben: Der bereits angelegte Job wechselt später
zu `failed`. Die Fehlermeldung steht in `GET /api/turns/{id}`.

## 7. Curl-Beispiel für Frontend-Entwickler

```bash
export BASE_URL='http://192.168.1.123:8000'
export COMPANION_TOKEN='TOKEN_AUS_DER_SERVER_KONFIG'

curl -fS "$BASE_URL/health"

curl -i -X POST "$BASE_URL/api/turns" \
  -H "Authorization: Bearer $COMPANION_TOKEN" \
  -H 'Content-Type: audio/wav' \
  --data-binary @aufnahme_16k_mono.wav

# ID aus der POST-Antwort übernehmen:
export TURN_ID='UUID_AUS_POST'
curl -sS -H "Authorization: Bearer $COMPANION_TOKEN" \
  "$BASE_URL/api/turns/$TURN_ID"

# Erst bei state=ready:
curl -fS -H "Authorization: Bearer $COMPANION_TOKEN" \
  -o antwort.wav "$BASE_URL/api/turns/$TURN_ID/audio.wav"
```

## 8. Aktuelle Grenzen (wichtig für die Weiterentwicklung)

- **Ein Turn = eine unabhängige Frage/Antwort.** Kein Gesprächsgedächtnis und
  keine serverseitige Session-ID.
- **Keine Echtzeit-Audiostreams** und keine WebSockets/SSE. Aufnehmen →
  hochladen → warten → Antwort herunterladen.
- **Ein Inferenz-Worker** verarbeitet Jobs nacheinander; weitere Jobs warten.
- **In-Memory-Jobverwaltung** und temporäre WAV-Dateien: Beim Neustart des
  Backend-Prozesses gehen alte Job-IDs/Antworten verloren.
- **Kein Abbrechen, Löschen, Wiederaufnehmen oder Fortschritt in Prozent.**
- **Keine Wakeword-Erkennung, keine Sprecheridentifikation, keine Tools/Actions.**
- **Kein Browser-CORS**, keine TLS-Verbindung, kein Pairing.
- Ausgabe ist immer die vollständig synthetisierte WAV-Datei, kein
  inkrementelles TTS-Streaming.

## 9. Vorschlag für API v0.2 (noch nicht implementiert)

Erst nach stabilem Audio-MVP sinnvoll:

1. `POST /api/sessions` mit mehrturnigem Gesprächskontext.
2. `DELETE /api/turns/{id}` zum Abbrechen und zur Jobbereinigung.
3. Ereignis-Stream (`SSE` oder `WebSocket`) statt Status-Polling.
4. Chunked Audio-Upload und TTS-Streaming für geringere Latenz.
5. Geräte-Pairing, HTTPS, Health/Capabilities-Endpoint und Versionierung
   `/api/v1/...`.

**Vertragsregel:** Die hier beschriebenen v0.1-Endpunkte bleiben der aktuelle
Implementierungsstand. Änderungen an Struktur oder Format zuerst im Backend
implementieren und testen, dann die Frontend-Dokumentation aktualisieren.

