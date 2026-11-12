"""Optional Ollama intent routing and local ComfyUI image generation.

No direct connection from ESP32 to ComfyUI is needed.
Workflow: ComfyUI 'Save (API Format)' JSON, with a CLIPTextEncode prompt node.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from io import BytesIO
import json
import os
from pathlib import Path
import secrets
import time
from uuid import uuid4

import httpx
from PIL import Image, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class Decision:
    mode: str                 # audio | image
    answer: str               # speech for audio, caption for image
    image_prompt: str = ""    # positive prompt for image only


def decide(text: str, history: list[dict[str, str]] | None = None) -> Decision:
    """A single structured Ollama call routes and generates the answer/prompt."""
    instructions = (
        "Du bist ein Intent-Router für ein deutschsprachiges Sprachgerät. "
        "Gib NUR JSON zurück mit 'mode' (audio|image), 'answer' und "
        "'image_prompt'. Wähle 'image' NUR wenn der Nutzer ein neues Bild, "
        "eine Illustration, ein Gemälde oder eine Zeichnung generieren lassen "
        "möchte. Sonst 'audio'. Bei audio: 'answer' ist die kurze direkt "
        "gesprochene Antwort (max. drei Sätze), 'image_prompt' ist leer. "
        "Bei image: 'answer' ist eine kurze deutsche Bildunterschrift; "
        "'image_prompt' ist eine konkrete bildliche Beschreibung auf Englisch "
        "mit wichtigen Details aus der Nutzeranfrage. Keine Markdown-Zeichen."
    )
    url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
    model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    messages = [
        {"role": "system", "content": instructions},
        *(history or []),
        {"role": "user", "content": text},
    ]
    schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["audio", "image"]},
            "answer": {"type": "string"},
            "image_prompt": {"type": "string"},
        },
        "required": ["mode", "answer", "image_prompt"],
        "additionalProperties": False,
    }
    with httpx.Client(timeout=180, trust_env=False) as client:
        response = client.post(url, json={"model": model, "stream": False,
                                          "format": schema,
                                          "options": {"temperature": 0},
                                          "messages": messages})
        response.raise_for_status()
        raw = response.json()["message"]["content"]
    try:
        data = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Ollama hat keine gültige JSON-Routingantwort geliefert") from exc
    if not isinstance(data, dict) or data.get("mode") not in ("audio", "image"):
        raise RuntimeError("Ollama hat keinen gültigen Antworttyp geliefert")
    answer = data.get("answer")
    prompt = data.get("image_prompt")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Ollama hat keine Antwort geliefert")
    if data["mode"] == "image":
        if not isinstance(prompt, str) or not prompt.strip():
            raise RuntimeError("Ollama hat keinen Bildprompt geliefert")
        return Decision("image", answer.strip(), prompt.strip())
    return Decision("audio", answer.strip())


def _workflow_for(prompt: str) -> dict:
    path = Path(os.getenv("COMFYUI_WORKFLOW_PATH", ""))
    if not str(path) or not path.is_file():
        raise RuntimeError("COMFYUI_WORKFLOW_PATH fehlt oder existiert nicht")
    workflow = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(workflow, dict):
        raise RuntimeError("ComfyUI-Workflow muss ein API-JSON-Objekt sein")
    workflow = deepcopy(workflow)
    node_id = os.getenv("COMFYUI_PROMPT_NODE", "").strip()
    if not node_id or node_id not in workflow:
        raise RuntimeError("COMFYUI_PROMPT_NODE ist nicht im API-Workflow vorhanden")
    node = workflow[node_id]
    if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict) or "text" not in node["inputs"]:
        raise RuntimeError("Prompt-Node hat kein inputs.text")
    node["inputs"]["text"] = prompt
    # Optional: randomize KSampler seed for a new image on each request.
    seed_node = os.getenv("COMFYUI_SEED_NODE", "").strip()
    if seed_node:
        seed_inputs = workflow.get(seed_node, {}).get("inputs", {})
        if "seed" not in seed_inputs:
            raise RuntimeError("COMFYUI_SEED_NODE hat kein inputs.seed")
        seed_inputs["seed"] = secrets.randbelow(2**32)
    return workflow


def _image_from_history(history: dict, prompt_id: str) -> dict | None:
    entry = history.get(prompt_id)
    if not isinstance(entry, dict):
        return None
    status = entry.get("status", {})
    if isinstance(status, dict) and status.get("status_str") == "error":
        raise RuntimeError("ComfyUI-Workflow fehlgeschlagen")
    outputs = entry.get("outputs", {})
    if not isinstance(outputs, dict):
        raise RuntimeError("ComfyUI hat ungültige Ausgaben geliefert")
    for node in outputs.values():
        if isinstance(node, dict):
            for result in node.get("images", []):
                if isinstance(result, dict) and result.get("filename"):
                    return result
    if isinstance(status, dict) and status.get("completed"):
        raise RuntimeError("ComfyUI hat keine Bilddatei erzeugt (SaveImage-Node prüfen)")
    return None


def generate_image(prompt: str, target: Path) -> None:
    """Queue configured workflow, await result, fetch output and save 480x480 JPEG."""
    base = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
    timeout = float(os.getenv("COMFYUI_TIMEOUT_SECONDS", "300"))
    if timeout <= 0 or timeout > 900:
        raise RuntimeError("COMFYUI_TIMEOUT_SECONDS muss zwischen 1 und 900 liegen")
    workflow = _workflow_for(prompt)
    client_id = str(uuid4())
    with httpx.Client(timeout=httpx.Timeout(20.0, read=60.0), trust_env=False) as client:
        result = client.post(base + "/prompt", json={"prompt": workflow, "client_id": client_id})
        result.raise_for_status()
        payload = result.json()
        if payload.get("node_errors"):
            raise RuntimeError(f"ComfyUI-Workflow ungültig: {str(payload['node_errors'])[:200]}")
        prompt_id = payload.get("prompt_id")
        if not isinstance(prompt_id, str) or not prompt_id:
            raise RuntimeError("ComfyUI hat keine prompt_id zurückgegeben")
        deadline = time.monotonic() + timeout
        image_info = None
        while time.monotonic() < deadline:
            history_response = client.get(base + f"/history/{prompt_id}")
            history_response.raise_for_status()
            image_info = _image_from_history(history_response.json(), prompt_id)
            if image_info:
                break
            time.sleep(1.5)
        if not image_info:
            raise TimeoutError("ComfyUI-Bildgenerierung hat das Zeitlimit überschritten")
        resp = client.get(base + "/view", params={
            "filename": image_info["filename"],
            "subfolder": image_info.get("subfolder", ""),
            "type": image_info.get("type", "output"),
        })
        resp.raise_for_status()
        data = resp.content
        if len(data) > 20 * 1024 * 1024:
            raise RuntimeError("ComfyUI-Bilddatei ist zu groß")
    try:
        with Image.open(BytesIO(data)) as src:
            if src.width * src.height > 32_000_000:
                raise RuntimeError("ComfyUI-Bilddimensionen sind zu groß")
            rgb = ImageOps.fit(src.convert("RGB"), (480, 480), method=Image.Resampling.LANCZOS)
            target.parent.mkdir(parents=True, exist_ok=True)
            rgb.save(target, "JPEG", quality=85, optimize=True)
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError("ComfyUI hat keine lesbare Bilddatei geliefert") from exc
