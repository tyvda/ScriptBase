#!/usr/bin/env python3
"""Patch the existing v0.4.1 Waveshare Companion app to support ComfyUI images.
Run inside the server directory or pass its path as the first argument.
"""
from pathlib import Path
import shutil
import sys

server = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
app = server / "app.py"
plugin = Path(__file__).resolve().parent / "server" / "multimodal.py"
if not app.is_file() or not (server / "pipeline.py").is_file():
    sys.exit("app.py / pipeline.py im angegebenen Server-Verzeichnis nicht gefunden")
s = app.read_text(encoding="utf8")
if 'version="0.5.0"' in s:
    sys.exit("v0.5.0 ist bereits installiert")
if 'version="0.4.1"' not in s:
    sys.exit("Erwartet Backend v0.4.1; keine Änderung vorgenommen")


def change(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("Unerwarteter Backend-Stand; Patch nicht angewendet: " + repr(old[:70]))
    s = s.replace(old, new, 1)

change('import pipeline\n', 'import pipeline\nimport multimodal\n')
change('version="0.4.1"', 'version="0.5.0"')
change('    answer: str = ""\n    error: str = ""',
       '    answer: str = ""\n    result_type: str = "audio"\n'
       '    image_prompt: str = ""\n    audio_url: str | None = None\n'
       '    image_url: str | None = None\n    error: str = ""')
change('''        session_id = get_turn(turn_id).session_id
        if session_id:
            answer = pipeline.generate_answer(transcript, conversation_history(session_id, turn_id))
        else:
            answer = pipeline.generate_answer(transcript)
        if not update_if_active(turn_id, answer=answer, state="speaking"):
            return
        pipeline.synthesize(answer, folder / "answer.wav")
        update_if_active(turn_id, state="ready")''',
'''        session_id = get_turn(turn_id).session_id
        history = conversation_history(session_id, turn_id) if session_id else None
        decision = multimodal.decide(transcript, history)
        if decision.mode == "image":
            if not update_if_active(turn_id, result_type="image", answer=decision.answer,
                                    image_prompt=decision.image_prompt, state="rendering"):
                return
            multimodal.generate_image(decision.image_prompt, folder / "image.jpg")
            update_if_active(turn_id, state="ready",
                             image_url=f"/api/turns/{turn_id}/image.jpg")
        else:
            if not update_if_active(turn_id, answer=decision.answer, state="speaking"):
                return
            pipeline.synthesize(decision.answer, folder / "answer.wav")
            update_if_active(turn_id, state="ready",
                             audio_url=f"/api/turns/{turn_id}/audio.wav")''')
change('''        "features": {"sessions": True, "cancel": True, "sse": True,
                     "audio_streaming": False, "job_persistence": False},''',
'''        "image_output": {"format": "jpeg", "width": 480, "height": 480},
        "features": {"sessions": True, "cancel": True, "sse": True,
                     "comfyui_images": True,
                     "audio_streaming": False, "job_persistence": False},''')
change('''def turn_audio(turn_id: str):
    turn = get_turn(turn_id)
    if turn.state != "ready":
        raise HTTPException(status_code=409, detail="Audio not ready")
    return FileResponse(_work_dir / turn_id / "answer.wav", media_type="audio/wav")''',
'''def turn_audio(turn_id: str):
    turn = get_turn(turn_id)
    if turn.state != "ready" or turn.result_type != "audio":
        raise HTTPException(status_code=409, detail="Audio not available for this turn")
    return FileResponse(_work_dir / turn_id / "answer.wav", media_type="audio/wav")


@app.get("/api/turns/{turn_id}/image.jpg")
def turn_image(turn_id: str):
    turn = get_turn(turn_id)
    if turn.state != "ready" or turn.result_type != "image":
        raise HTTPException(status_code=409, detail="Image not available for this turn")
    return FileResponse(_work_dir / turn_id / "image.jpg", media_type="image/jpeg")''')
# no writes until every replacement was checked
backup = app.with_name("app.py.before-comfyui")
if backup.exists():
    sys.exit("Backup-Datei existiert bereits: " + str(backup))
shutil.copy2(app, backup)
shutil.copy2(plugin, server / "multimodal.py")
app.write_text(s, encoding="utf8")
print("Patch erfolgreich. Sicherung:", backup)
print("Nächste Schritte: Pillow installieren, ComfyUI-Workflow konfigurieren, Service neu starten")
