"""Asynchronous LAN bridge between ESP32 audio and local AI tools."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import io
import threading
from uuid import uuid4
import wave

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse

import pipeline


app = FastAPI(title="Local Companion Bridge", version="0.2.0")

# This MVP intentionally serializes inference to avoid exhausting a local GPU.
_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="companion-ai")
_lock = threading.RLock()
_store = TemporaryDirectory(prefix="companion-mvp-")
_work_dir = Path(_store.name)
_max_bytes = 44 + 16000 * 2 * 20  # up to 20 seconds of mono PCM


@dataclass
class Turn:
    id: str
    state: str = "queued"
    transcript: str = ""
    answer: str = ""
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


_turns: dict[str, Turn] = {}


def validate_wav(data: bytes) -> None:
    try:
        with wave.open(io.BytesIO(data), "rb") as f:
            if (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getcomptype()) != (1, 2, 16000, "NONE"):
                raise ValueError("Expected 16 kHz, 16-bit, mono PCM WAV")
            if not 0 < f.getnframes() <= 16000 * 20:
                raise ValueError("Audio must be between 1 sample and 20 seconds")
            # Reject truncated recordings; wave.open alone does not validate payload length.
            if len(f.readframes(f.getnframes())) != f.getnframes() * 2:
                raise ValueError("Truncated WAV audio")
    except (EOFError, wave.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def update(turn_id: str, **fields: str) -> None:
    with _lock:
        turn = _turns[turn_id]
        for key, value in fields.items():
            setattr(turn, key, value)


def work(turn_id: str) -> None:
    folder = _work_dir / turn_id
    try:
        update(turn_id, state="transcribing")
        transcript = pipeline.transcribe(folder / "input.wav")
        if not transcript:
            raise RuntimeError("Keine Sprache erkannt – bitte erneut aufnehmen")
        update(turn_id, transcript=transcript, state="thinking")
        answer = pipeline.generate_answer(transcript)
        update(turn_id, answer=answer, state="speaking")
        pipeline.synthesize(answer, folder / "answer.wav")
        update(turn_id, state="ready")
    except Exception as exc:
        update(turn_id, state="failed", error=str(exc)[:300])


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/turns", status_code=202)
async def create_turn(request: Request):
    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "audio/wav":
        raise HTTPException(status_code=415, detail="Content-Type must be audio/wav")

    # Bound memory even if the client omits Content-Length.
    chunks = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > _max_bytes:
            raise HTTPException(status_code=413, detail="Recording exceeds 20 seconds")
        chunks.append(chunk)
    data = b"".join(chunks)
    validate_wav(data)

    turn_id = str(uuid4())
    folder = _work_dir / turn_id
    folder.mkdir()
    (folder / "input.wav").write_bytes(data)
    with _lock:
        _turns[turn_id] = Turn(id=turn_id)
    _pool.submit(work, turn_id)

    if request.query_params.get("plain") == "1":
        return PlainTextResponse(turn_id, status_code=202)
    return {"id": turn_id, "state": "queued"}


def get_turn(turn_id: str) -> Turn:
    with _lock:
        turn = _turns.get(turn_id)
        if turn is None:
            raise HTTPException(status_code=404, detail="Unknown turn")
        # A snapshot, not the mutable shared object.
        return Turn(**vars(turn))


@app.get("/api/turns/{turn_id}")
def turn_status(turn_id: str):
    return vars(get_turn(turn_id))


@app.get("/api/turns/{turn_id}/state")
def turn_state(turn_id: str):
    return PlainTextResponse(get_turn(turn_id).state)


@app.get("/api/turns/{turn_id}/audio.wav")
def turn_audio(turn_id: str):
    turn = get_turn(turn_id)
    if turn.state != "ready":
        raise HTTPException(status_code=409, detail="Audio not ready")
    return FileResponse(_work_dir / turn_id / "answer.wav", media_type="audio/wav")

