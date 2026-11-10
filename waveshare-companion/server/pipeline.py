"""Local speech-to-text -> LLM -> text-to-speech pipeline.

The ESP32 never talks to Ollama directly: its sole peer is our LAN HTTP server.
Dependencies/models are only loaded when a turn is processed.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import threading
import wave

import httpx


_model = None
_model_lock = threading.Lock()


def transcribe(input_wav: Path) -> str:
    """Transcribe a mono 16 kHz WAV locally with faster-whisper."""
    global _model
    with _model_lock:
        if _model is None:
            from faster_whisper import WhisperModel

            _model = WhisperModel(
                os.getenv("WHISPER_MODEL", "small"),
                device=os.getenv("WHISPER_DEVICE", "cpu"),
                compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
            )
        # Iterating segments performs the actual model inference.
        segments, _ = _model.transcribe(str(input_wav), language="de", vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()


def generate_answer(user_text: str, history: list[dict[str, str]] | None = None) -> str:
    """Use Ollama; the optional session history is bounded by the API layer."""
    url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
    model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    messages = [
        {
            "role": "system",
            "content": (
                "Du bist ein hilfreicher deutschsprachiger Begleiter auf "
                "einem kleinen Sprachgerät. Antworte präzise, freundlich "
                "und mit maximal drei kurzen Sätzen."
            ),
        },
        *(history or []),
        {"role": "user", "content": user_text},
    ]
    with httpx.Client(timeout=180.0, trust_env=False) as client:
        response = client.post(
            url,
            json={
                "model": model,
                "stream": False,
                "messages": messages,
            },
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"].strip()
        if not answer:
            raise RuntimeError("Das LLM hat eine leere Antwort erzeugt")
        return answer


def synthesize(answer: str, output_wav: Path) -> None:
    """Run local Piper, resample to 16 kHz PCM, write a canonical WAV header."""
    model = os.getenv("PIPER_MODEL", "")
    if not model or not Path(model).is_file():
        raise RuntimeError("PIPER_MODEL muss auf eine vorhandene .onnx-Datei zeigen")

    piper_wav = output_wav.with_name("piper_original.wav")
    raw_pcm = output_wav.with_name("response.raw")
    try:
        subprocess.run(
            [sys.executable, "-m", "piper", "-m", model, "-f", str(piper_wav), "--", answer],
            capture_output=True,
            check=True,
            timeout=120,
        )
        subprocess.run(
            [
                "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(piper_wav),
                "-f", "s16le", "-ac", "1", "-ar", "16000", str(raw_pcm),
            ],
            capture_output=True,
            check=True,
            timeout=120,
        )
        with wave.open(str(output_wav), "wb") as dst:
            dst.setnchannels(1)
            dst.setsampwidth(2)
            dst.setframerate(16000)
            with raw_pcm.open("rb") as src:
                while chunk := src.read(64 * 1024):
                    dst.writeframesraw(chunk)
    finally:
        piper_wav.unlink(missing_ok=True)
        raw_pcm.unlink(missing_ok=True)

