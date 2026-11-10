/*
 * Waveshare ESP32-S3-Touch-AMOLED-2.16 local voice companion (audio MVP).
 *
 * Arduino-ESP32 3.3.x. Requires vendor audio driver files; see README.
 * Hardware integration is a starting point and MUST be tested on the board.
 *
 * Hold KEY3 (GPIO18) to speak; release to upload the recording.
 * The server responds asynchronously. The board polls and plays its WAV.
 */

#include <Arduino.h>
#include <ESP_I2S.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <Wire.h>
#include "esp_check.h"
#include "es7210.h"
#include "es8311.h"
#include "secrets.h"

static constexpr int kButton = 18;
static constexpr int kAmpPin = 46;
static constexpr int kI2sMclk = 42;
static constexpr int kI2sBclk = 9;
static constexpr int kI2sWs = 45;
static constexpr int kI2sMicData = 10;
static constexpr int kI2sSpeakerData = 8;
static constexpr uint32_t kSampleRate = 16000;
static constexpr size_t kMaxSamples = 12 * kSampleRate;
static constexpr size_t kWavHeaderSize = 44;

I2SClass i2s;
uint8_t *wavBuffer = nullptr;  // 44-byte WAV header + 16-bit mono samples, in PSRAM
es8311_handle_t speakerCodec = nullptr;

static void writeU16(uint8_t *p, uint16_t v) {
  p[0] = v & 0xff;
  p[1] = v >> 8;
}

static void writeU32(uint8_t *p, uint32_t v) {
  p[0] = v & 0xff;
  p[1] = (v >> 8) & 0xff;
  p[2] = (v >> 16) & 0xff;
  p[3] = (v >> 24) & 0xff;
}

static void makeWavHeader(size_t samples) {
  const uint32_t audioBytes = samples * sizeof(int16_t);
  memcpy(wavBuffer, "RIFF", 4);
  writeU32(wavBuffer + 4, 36 + audioBytes);
  memcpy(wavBuffer + 8, "WAVEfmt ", 8);
  writeU32(wavBuffer + 16, 16);          // fmt chunk size
  writeU16(wavBuffer + 20, 1);           // PCM
  writeU16(wavBuffer + 22, 1);           // mono
  writeU32(wavBuffer + 24, kSampleRate);
  writeU32(wavBuffer + 28, kSampleRate * 2);
  writeU16(wavBuffer + 32, 2);           // block align
  writeU16(wavBuffer + 34, 16);          // bits/sample
  memcpy(wavBuffer + 36, "data", 4);
  writeU32(wavBuffer + 40, audioBytes);
}

static bool beginAudio() {
  Wire.begin(15, 14);  // Shared board I2C: SDA 15, SCL 14

  i2s.setPins(kI2sBclk, kI2sWs, kI2sSpeakerData, kI2sMicData, kI2sMclk);
  if (!i2s.begin(I2S_MODE_STD, kSampleRate, I2S_DATA_BIT_WIDTH_16BIT,
                 I2S_SLOT_MODE_STEREO, I2S_STD_SLOT_BOTH)) {
    Serial.println("I2S init failed");
    return false;
  }

  // Based on vendor example 06_ES7210 (external ADC / microphone array).
  audio_hal_codec_config_t micCfg = {
    .adc_input = AUDIO_HAL_ADC_INPUT_ALL,
    .codec_mode = AUDIO_HAL_CODEC_MODE_ENCODE,
    .i2s_iface = {
      .mode = AUDIO_HAL_MODE_SLAVE,
      .fmt = AUDIO_HAL_I2S_NORMAL,
      .samples = AUDIO_HAL_16K_SAMPLES,
      .bits = AUDIO_HAL_BIT_LENGTH_16BITS,
    },
  };
  if (es7210_adc_init(&Wire, &micCfg) != ESP_OK ||
      es7210_adc_config_i2s(micCfg.codec_mode, &micCfg.i2s_iface) != ESP_OK ||
      es7210_adc_ctrl_state(micCfg.codec_mode, AUDIO_HAL_CTRL_START) != ESP_OK) {
    Serial.println("ES7210 init failed");
    return false;
  }
  es7210_adc_set_gain((es7210_input_mics_t)(ES7210_INPUT_MIC1 | ES7210_INPUT_MIC2), GAIN_0DB);
  es7210_adc_set_gain((es7210_input_mics_t)(ES7210_INPUT_MIC3 | ES7210_INPUT_MIC4), GAIN_37_5DB);

  // Based on vendor example 07_ES8311 (speaker codec / amp path).
  speakerCodec = es8311_create(0, ES8311_ADDRRES_0);
  if (!speakerCodec) return false;
  es8311_clock_config_t clk = {
    .mclk_inverted = false,
    .sclk_inverted = false,
    .mclk_from_mclk_pin = true,
    .mclk_frequency = (int)(kSampleRate * 256),
    .sample_frequency = (int)kSampleRate,
  };
  if (es8311_init(speakerCodec, &clk, ES8311_RESOLUTION_16, ES8311_RESOLUTION_16) != ESP_OK)
    return false;
  es8311_voice_volume_set(speakerCodec, 70, nullptr);

  // This follows the manufacturer's demo. Verify PA behavior on your revision.
  pinMode(kAmpPin, OUTPUT);
  digitalWrite(kAmpPin, HIGH);
  return true;
}

static size_t recordWhilePressed() {
  Serial.println("Recording...");
  size_t count = 0;
  int16_t *mono = reinterpret_cast<int16_t *>(wavBuffer + kWavHeaderSize);
  int16_t stereo[512];

  while (digitalRead(kButton) == LOW && count < kMaxSamples) {
    const size_t got = i2s.readBytes(reinterpret_cast<char *>(stereo), sizeof(stereo));
    // Select the first I2S slot as a mono microphone track.
    // TODO on hardware: inspect both slots/RMS and adjust channel if needed.
    const size_t frames = got / (2 * sizeof(int16_t));
    for (size_t frame = 0; frame < frames && count < kMaxSamples; ++frame) {
      mono[count++] = stereo[frame * 2];
    }
  }
  makeWavHeader(count);
  Serial.printf("Captured %u samples (%.2f s)\n", (unsigned)count,
                (float)count / kSampleRate);
  return count;
}

static bool requestText(const String &path, String &response) {
  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, String(SERVER_BASE_URL) + path)) return false;
  http.setTimeout(10000);
  const int status = http.GET();
  if (status == 200) response = http.getString();
  else Serial.printf("GET %s => HTTP %d\n", path.c_str(), status);
  http.end();
  return status == 200;
}

static String upload(size_t samples) {
  if (WiFi.status() != WL_CONNECTED) return "";
  WiFiClient client;
  HTTPClient http;
  const String endpoint = String(SERVER_BASE_URL) + "/api/turns?plain=1";
  if (!http.begin(client, endpoint)) return "";
  http.setTimeout(15000);
  http.addHeader("Content-Type", "audio/wav");
  const int status = http.POST(wavBuffer, kWavHeaderSize + samples * 2);
  const String id = status == 202 ? http.getString() : "";
  Serial.printf("Upload HTTP %d, turn: %s\n", status, id.c_str());
  http.end();
  return id;
}

static bool playReply(const String &turnId) {
  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, String(SERVER_BASE_URL) + "/api/turns/" + turnId + "/audio.wav"))
    return false;
  http.setTimeout(10000);
  const int status = http.GET();
  if (status != 200) {
    Serial.printf("Audio HTTP %d\n", status);
    http.end();
    return false;
  }

  Stream *stream = http.getStreamPtr();
  uint8_t header[44];
  bool valid = stream->readBytes(reinterpret_cast<char *>(header), sizeof(header)) == sizeof(header);
  valid = valid && !memcmp(header, "RIFF", 4) && !memcmp(header + 8, "WAVEfmt ", 8) &&
          !memcmp(header + 36, "data", 4) && header[22] == 1 && header[23] == 0 &&
          header[34] == 16 && header[35] == 0 &&
          (uint32_t)header[24] + ((uint32_t)header[25] << 8) +
              ((uint32_t)header[26] << 16) + ((uint32_t)header[27] << 24) == 16000;
  if (!valid) {
    Serial.println("Unexpected WAV header (expected canonical 16k/16-bit/mono)");
    http.end();
    return false;
  }

  uint32_t remaining = (uint32_t)header[40] | ((uint32_t)header[41] << 8) |
                       ((uint32_t)header[42] << 16) | ((uint32_t)header[43] << 24);
  int16_t mono[256];
  int16_t stereo[512];
  Serial.printf("Playing %u bytes\n", (unsigned)remaining);

  while (remaining > 0 && http.connected()) {
    const size_t request = min((size_t)remaining, sizeof(mono));
    const size_t got = stream->readBytes(reinterpret_cast<char *>(mono), request);
    if (got == 0) break;
    const size_t frames = got / sizeof(int16_t);
    for (size_t i = 0; i < frames; ++i) {
      stereo[2 * i] = mono[i];
      stereo[2 * i + 1] = mono[i];
    }
    i2s.write(reinterpret_cast<uint8_t *>(stereo), frames * 2 * sizeof(int16_t));
    remaining -= got;
  }
  http.end();
  return remaining == 0;
}

static void waitForAnswer(const String &id) {
  const uint32_t started = millis();
  while (millis() - started < 180000) {
    String state;
    if (!requestText("/api/turns/" + id + "/state", state)) break;
    state.trim();
    Serial.printf("Server state: %s\n", state.c_str());
    if (state == "ready") {
      Serial.println(playReply(id) ? "Playback completed" : "Playback error");
      return;
    }
    if (state == "failed") {
      Serial.println("Server job failed; see GET /api/turns/{id} for details");
      return;
    }
    delay(1200);
  }
  Serial.println("Request timed out / connection lost");
}

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(kButton, INPUT_PULLUP);

  wavBuffer = reinterpret_cast<uint8_t *>(ps_malloc(kWavHeaderSize + kMaxSamples * 2));
  if (!wavBuffer) {
    Serial.println("PSRAM missing – enable PSRAM in board options");
    while (true) delay(1000);
  }
  if (!beginAudio()) {
    Serial.println("Audio setup failed – verify vendor examples 06 and 07 separately");
    while (true) delay(1000);
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting Wi-Fi");
  uint32_t since = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - since < 30000) {
    delay(300);
    Serial.print(".");
  }
  Serial.printf("\nWi-Fi: %s IP: %s\n",
                WiFi.status() == WL_CONNECTED ? "connected" : "offline",
                WiFi.localIP().toString().c_str());
  Serial.println("Hold KEY3 to record and release to send.");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(1000);
    return;
  }
  if (digitalRead(kButton) != LOW) {
    delay(25);
    return;
  }
  delay(35);  // debounce
  if (digitalRead(kButton) != LOW) return;
  const size_t samples = recordWhilePressed();
  if (samples > kSampleRate / 4) {
    const String id = upload(samples);
    if (!id.isEmpty()) waitForAnswer(id);
  } else {
    Serial.println("Recording too short");
  }
  while (digitalRead(kButton) == LOW) delay(30);  // wait for release
}

