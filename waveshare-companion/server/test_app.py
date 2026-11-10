"""Run with: python -m unittest -v test_app  (from server/)"""

import io
import threading
import unittest
from unittest.mock import patch
import wave

from fastapi.testclient import TestClient

import app


def make_wav(frames=1600, rate=16000):
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\0\0" * frames)
    return output.getvalue()


class ApiTests(unittest.TestCase):
    def setUp(self):
        app._pool.submit(lambda: None).result(timeout=2)
        with app._lock:
            app._turns.clear()
            app._sessions.clear()
        self.client = TestClient(app.app)
        self.headers = {"Content-Type": "audio/wav"}

    def test_format_validation_without_authentication(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.post("/api/turns", content=make_wav()).status_code, 415)
        invalid = self.client.post("/api/turns", content=make_wav(rate=44100), headers=self.headers)
        self.assertEqual(invalid.status_code, 422)
        oversized = self.client.post("/api/turns", content=b"x" * 700000, headers=self.headers)
        self.assertEqual(oversized.status_code, 413)
        malformed = self.client.post("/api/turns", content=b"abc", headers=self.headers)
        self.assertEqual(malformed.status_code, 422)

    def test_async_turn_and_audio_download(self):
        fake_result = make_wav()

        def fake_synthesize(text, target):
            target.write_bytes(fake_result)

        with patch.object(app.pipeline, "transcribe", return_value="Hallo"), \
             patch.object(app.pipeline, "generate_answer", return_value="Guten Tag"), \
             patch.object(app.pipeline, "synthesize", side_effect=fake_synthesize):
            upload = self.client.post("/api/turns?plain=1", content=make_wav(), headers=self.headers)
            self.assertEqual(upload.status_code, 202)
            turn_id = upload.text
            # Wait only for the mocked background worker to finish.
            app._pool.submit(lambda: None).result(timeout=2)
            status = self.client.get(f"/api/turns/{turn_id}", headers=self.headers).json()
            self.assertEqual(status["state"], "ready")
            self.assertEqual(status["transcript"], "Hallo")
            audio = self.client.get(f"/api/turns/{turn_id}/audio.wav", headers=self.headers)
            self.assertEqual(audio.status_code, 200)
            self.assertEqual(audio.content, fake_result)

    def test_unknown_turn(self):
        result = self.client.get("/api/turns/not-found/state", headers=self.headers)
        self.assertEqual(result.status_code, 404)

    def test_status_and_audio_do_not_require_token(self):
        spec = self.client.get("/openapi.json").json()
        self.assertNotIn("securitySchemes", spec.get("components", {}))
        with app._lock:
            app._turns["test-no-auth"] = app.Turn(id="test-no-auth", state="queued")
        self.assertEqual(self.client.get("/api/turns/test-no-auth").status_code, 200)
        self.assertEqual(self.client.get("/api/turns/test-no-auth/state").text, "queued")
        self.assertEqual(self.client.get("/api/turns/test-no-auth/audio.wav").status_code, 409)

    def test_capabilities_and_readiness(self):
        response = self.client.get("/api/capabilities")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["protocol_version"], "0.3.0")
        self.assertFalse(response.json()["authentication_required"])
        with patch.object(app, "check_readiness", return_value={"ready": False, "components": {"ollama": False}}):
            self.assertEqual(self.client.get("/ready").status_code, 503)
        with patch.object(app, "check_readiness", return_value={"ready": True, "components": {"ollama": True}}):
            self.assertEqual(self.client.get("/ready").status_code, 200)

    def test_cancellation_and_queue_limit(self):
        blocked = threading.Event()
        blocker = app._pool.submit(lambda: blocked.wait(5))
        old_limit = app._max_pending
        try:
            app._max_pending = 1
            first = self.client.post("/api/turns", content=make_wav(), headers=self.headers)
            turn_id = first.json()["id"]
            self.assertEqual(self.client.post("/api/turns", content=make_wav(),
                                              headers=self.headers).status_code, 429)
            cancelled = self.client.delete(f"/api/turns/{turn_id}")
            self.assertEqual(cancelled.json()["state"], "cancelled")
            self.assertEqual(self.client.get(f"/api/turns/{turn_id}/audio.wav").status_code, 409)
            self.assertEqual(self.client.delete(f"/api/turns/{turn_id}").json()["state"], "cancelled")
            self.assertEqual(self.client.get(f"/api/turns/{turn_id}/state").text, "cancelled")
        finally:
            app._max_pending = old_limit
            blocked.set()
            blocker.result(timeout=2)
            app._pool.submit(lambda: None).result(timeout=2)

    def test_sse_delivers_terminal_state_without_auth(self):
        with app._lock:
            app._turns["finished"] = app.Turn(id="finished", state="ready", answer="Hallo")
        stream = self.client.get("/api/turns/finished/events")
        self.assertEqual(stream.status_code, 200)
        self.assertIn("text/event-stream", stream.headers["content-type"])
        self.assertIn("event: state", stream.text)
        self.assertIn('"state": "ready"', stream.text)
        self.assertEqual(self.client.get("/api/turns/unknown/events").status_code, 404)

    def test_sessions_and_conversation_history(self):
        session_result = self.client.post("/api/sessions", json={"label": "Wave"})
        self.assertEqual(session_result.status_code, 201)
        sid = session_result.json()["id"]
        self.assertEqual(self.client.get(f"/api/sessions/{sid}").json()["turn_count"], 0)
        self.assertEqual(self.client.post("/api/turns?session_id=missing", content=make_wav(),
                                          headers=self.headers).status_code, 404)

        def fake_synthesize(text, target):
            target.write_bytes(make_wav())

        with patch.object(app.pipeline, "transcribe", side_effect=["Ich heiße Sebastian", "Wie heiße ich?"]), \
             patch.object(app.pipeline, "generate_answer", side_effect=["Hallo Sebastian", "Sebastian"]) as generated, \
             patch.object(app.pipeline, "synthesize", side_effect=fake_synthesize):
            first = self.client.post(f"/api/turns?session_id={sid}", content=make_wav(), headers=self.headers)
            self.assertEqual(first.status_code, 202)
            app._pool.submit(lambda: None).result(timeout=2)
            second = self.client.post(f"/api/turns?session_id={sid}", content=make_wav(), headers=self.headers)
            self.assertEqual(second.status_code, 202)
            app._pool.submit(lambda: None).result(timeout=2)
            self.assertEqual(generated.call_count, 2)
            self.assertEqual(generated.call_args_list[0].args[1], [])
            self.assertEqual(generated.call_args_list[1].args[1], [
                {"role": "user", "content": "Ich heiße Sebastian"},
                {"role": "assistant", "content": "Hallo Sebastian"},
            ])
        history = self.client.get(f"/api/sessions/{sid}/turns").json()["turns"]
        self.assertEqual(len(history), 2)
        self.assertTrue(all(t["session_id"] == sid for t in history))

    def test_cancel_during_transcription_does_not_publish_answer(self):
        entered = threading.Event()
        release = threading.Event()

        def slow_transcribe(_):
            entered.set()
            release.wait(3)
            return "Hallo"

        with patch.object(app.pipeline, "transcribe", side_effect=slow_transcribe), \
             patch.object(app.pipeline, "generate_answer") as generated, \
             patch.object(app.pipeline, "synthesize") as synthesized:
            try:
                response = self.client.post("/api/turns", content=make_wav(), headers=self.headers)
                tid = response.json()["id"]
                self.assertTrue(entered.wait(2))
                self.assertEqual(self.client.delete(f"/api/turns/{tid}").json()["state"], "cancelled")
            finally:
                release.set()
                app._pool.submit(lambda: None).result(timeout=3)
            self.assertEqual(self.client.get(f"/api/turns/{tid}").json()["state"], "cancelled")
            generated.assert_not_called()
            synthesized.assert_not_called()


if __name__ == "__main__":
    unittest.main()
