"""Asynchronous audio bridge with optional conversational sessions and events."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import io
import threading
from uuid import uuid4
import wave

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field
import httpx

import pipeline


app = FastAPI(title="Local Companion Bridge", version="0.4.0")

# This MVP intentionally serializes inference to avoid exhausting a local GPU.
_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="companion-ai")
_lock = threading.RLock()
_store = TemporaryDirectory(prefix="companion-mvp-")
_work_dir = Path(_store.name)
_max_seconds = 10
_sample_rate = 16000
_max_bytes = 44 + _sample_rate * 2 * _max_seconds  # max 320044 bytes
_max_pending = 8  # At most 8 queued/running turns, even on an unauthenticated LAN.
_history_turns = 8  # Last 8 completed exchanges per conversational session.
_terminal = frozenset({"ready", "failed", "cancelled"})


@dataclass
class Turn:
    id: str
    session_id: str | None = None
    state: str = "queued"
    transcript: str = ""
    answer: str = ""
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


_turns: dict[str, Turn] = {}
_futures: dict[str, Future] = {}


@dataclass
class Session:
    id: str
    label: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    turn_ids: list[str] = field(default_factory=list)


class SessionCreate(BaseModel):
    label: str = Field(default="", max_length=80)


_sessions: dict[str, Session] = {}


def validate_wav(data: bytes) -> None:
    try:
        with wave.open(io.BytesIO(data), "rb") as f:
            if (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getcomptype()) != (1, 2, 16000, "NONE"):
                raise ValueError("Expected 16 kHz, 16-bit, mono PCM WAV")
            if not 0 < f.getnframes() <= _sample_rate * _max_seconds:
                raise ValueError("Audio must be between 1 sample and 10 seconds")
            # Reject truncated recordings; wave.open alone does not validate payload length.
            if len(f.readframes(f.getnframes())) != f.getnframes() * 2:
                raise ValueError("Truncated WAV audio")
    except (EOFError, wave.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def update_if_active(turn_id: str, **fields: str) -> bool:
    """Apply a worker transition unless the client already cancelled the job."""
    with _lock:
        turn = _turns[turn_id]
        if turn.state == "cancelled":
            return False
        for key, value in fields.items():
            setattr(turn, key, value)
        return True


def conversation_history(session_id: str, before_turn_id: str) -> list[dict[str, str]]:
    """Gather prior successful exchanges, newest first, without leaking sessions."""
    with _lock:
        history: list[dict[str, str]] = []
        for previous_id in _sessions[session_id].turn_ids:
            if previous_id == before_turn_id:
                break
            previous = _turns[previous_id]
            if previous.state == "ready":
                history.extend([
                    {"role": "user", "content": previous.transcript},
                    {"role": "assistant", "content": previous.answer},
                ])
        return history[-2 * _history_turns:]


def work(turn_id: str) -> None:
    folder = _work_dir / turn_id
    try:
        if not update_if_active(turn_id, state="transcribing"):
            return
        transcript = pipeline.transcribe(folder / "input.wav")
        if not transcript:
            raise RuntimeError("Keine Sprache erkannt – bitte erneut aufnehmen")
        if not update_if_active(turn_id, transcript=transcript, state="thinking"):
            return
        session_id = get_turn(turn_id).session_id
        if session_id:
            answer = pipeline.generate_answer(transcript, conversation_history(session_id, turn_id))
        else:
            answer = pipeline.generate_answer(transcript)
        if not update_if_active(turn_id, answer=answer, state="speaking"):
            return
        pipeline.synthesize(answer, folder / "answer.wav")
        update_if_active(turn_id, state="ready")
    except Exception as exc:
        update_if_active(turn_id, state="failed", error=str(exc)[:300])


def _session_view(session: Session) -> dict:
    return {"id": session.id, "label": session.label,
            "created_at": session.created_at, "turn_count": len(session.turn_ids)}


def get_session(session_id: str) -> Session:
    with _lock:
        session = _sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Unknown session")
        return Session(**asdict(session))


def check_readiness() -> dict:
    """Lightweight checks. Whisper model downloads remain lazy until first use."""
    model_path = os.getenv("PIPER_MODEL", "")
    checks = {
        "whisper_installed": importlib.util.find_spec("faster_whisper") is not None,
        "piper_model": bool(model_path) and Path(model_path).is_file(),
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ollama": False,
    }
    url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/tags"
    configured_model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    try:
        with httpx.Client(timeout=3.0, trust_env=False) as client:
            response = client.get(url)
            response.raise_for_status()
            checks["ollama"] = any(m.get("name") == configured_model or
                                   m.get("model") == configured_model
                                   for m in response.json().get("models", []))
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        pass
    return {"ready": all(checks.values()), "components": checks}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/ready")
def ready():
    status = check_readiness()
    if not status["ready"]:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content=status)
    return status


@app.get("/api/capabilities")
def capabilities():
    return {
        "protocol_version": "0.4.0", "authentication_required": False,
        "audio_input": {"format": "wav", "codec": "pcm_s16le", "sample_rate": 16000,
                        "channels": 1, "max_seconds": _max_seconds, "max_bytes": _max_bytes},
        "audio_output": {"format": "wav", "codec": "pcm_s16le", "sample_rate": 16000,
                         "channels": 1},
        "features": {"sessions": True, "cancel": True, "sse": True,
                     "audio_streaming": False, "job_persistence": False},
    }


@app.post("/api/sessions", status_code=201)
def create_session(payload: SessionCreate | None = None):
    session = Session(id=str(uuid4()), label=payload.label if payload else "")
    with _lock:
        _sessions[session.id] = session
    return _session_view(session)


@app.get("/api/sessions/{session_id}")
def session_status(session_id: str):
    return _session_view(get_session(session_id))


@app.get("/api/sessions/{session_id}/turns")
def session_turns(session_id: str):
    with _lock:
        session = get_session(session_id)
        return {"session_id": session_id,
                "turns": [asdict(_turns[turn_id]) for turn_id in session.turn_ids]}


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
            raise HTTPException(status_code=413, detail="Recording exceeds 10 seconds")
        chunks.append(chunk)
    data = b"".join(chunks)
    validate_wav(data)

    session_id = request.query_params.get("session_id") or None
    with _lock:
        if session_id and session_id not in _sessions:
            raise HTTPException(status_code=404, detail="Unknown session")
        if sum(turn.state not in _terminal for turn in _turns.values()) >= _max_pending:
            raise HTTPException(status_code=429, detail="Too many pending turns")
        turn_id = str(uuid4())
        folder = _work_dir / turn_id
        folder.mkdir()
        (folder / "input.wav").write_bytes(data)
        _turns[turn_id] = Turn(id=turn_id, session_id=session_id)
        if session_id:
            _sessions[session_id].turn_ids.append(turn_id)
        future = _pool.submit(work, turn_id)
        _futures[turn_id] = future
        future.add_done_callback(lambda _, tid=turn_id: discard_future(tid))

    if request.query_params.get("plain") == "1":
        return PlainTextResponse(turn_id, status_code=202)
    return {"id": turn_id, "state": "queued"}


def discard_future(turn_id: str) -> None:
    with _lock:
        _futures.pop(turn_id, None)


def get_turn(turn_id: str) -> Turn:
    with _lock:
        turn = _turns.get(turn_id)
        if turn is None:
            raise HTTPException(status_code=404, detail="Unknown turn")
        # A snapshot, not the mutable shared object.
        return Turn(**asdict(turn))


@app.get("/api/turns/{turn_id}")
def turn_status(turn_id: str):
    return asdict(get_turn(turn_id))


@app.get("/api/turns/{turn_id}/state")
def turn_state(turn_id: str):
    return PlainTextResponse(get_turn(turn_id).state)


@app.get("/api/turns/{turn_id}/audio.wav")
def turn_audio(turn_id: str):
    turn = get_turn(turn_id)
    if turn.state != "ready":
        raise HTTPException(status_code=409, detail="Audio not ready")
    return FileResponse(_work_dir / turn_id / "answer.wav", media_type="audio/wav")


@app.delete("/api/turns/{turn_id}")
def cancel_turn(turn_id: str):
    with _lock:
        turn = _turns.get(turn_id)
        if turn is None:
            raise HTTPException(status_code=404, detail="Unknown turn")
        if turn.state not in _terminal:
            turn.state = "cancelled"
            turn.error = "Cancelled by client"
            future = _futures.get(turn_id)
            if future is not None:
                future.cancel()
        # Terminal turns are unchanged; DELETE is safe to repeat.
        return asdict(turn)


@app.get("/api/turns/{turn_id}/events")
async def turn_events(turn_id: str, request: Request):
    get_turn(turn_id)  # Return a regular HTTP 404 before opening the stream.

    async def event_stream():
        last_state = None
        ticks = 0
        while True:
            turn = get_turn(turn_id)
            signature = (turn.state, turn.transcript, turn.answer, turn.error)
            if signature != last_state:
                yield "event: state\ndata: " + json.dumps(asdict(turn), ensure_ascii=False) + "\n\n"
                last_state = signature
            if turn.state in _terminal or await request.is_disconnected():
                break
            ticks += 1
            if ticks % 30 == 0:
                yield ": keepalive\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

