from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import hashlib, os, shutil, uuid
from .timeline import Timeline
from .engine import parse_instruction

app = FastAPI(title="IncuBrix Prompt-Based Video Editing Engine MVP", version="0.1.0")
DATA = Path(os.getenv("DATA_DIR", "/data"))
DATA.mkdir(parents=True, exist_ok=True)
sessions = {}

class Instruction(BaseModel):
    say: str

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/ready")
def ready(): return {"status":"ready"}

@app.post("/api/v1/videos")
async def upload_video(file: UploadFile = File(...)):
    if Path(file.filename or "").suffix.lower() not in (".mp4", ".mov"):
        raise HTTPException(400, detail={"error":{"code":"UNSUPPORTED_FORMAT","message":"Upload MP4 or MOV","retryable":False,"details":{}}})
    vid = str(uuid.uuid4()); path = DATA / f"{vid}{Path(file.filename).suffix.lower()}"
    digest = hashlib.sha256()
    with path.open("wb") as out:
        while chunk := await file.read(1024*1024):
            digest.update(chunk); out.write(chunk)
    # Duration extraction is intentionally delegated to ffprobe in the render-ready version.
    sessions[vid] = {"path":str(path), "sha256":digest.hexdigest(), "timeline":None}
    return {"video_id":vid, "filename":file.filename, "sha256":digest.hexdigest(),
            "message":"Upload stored. Create a session with a known duration using /api/v1/sessions."}

class SessionCreate(BaseModel):
    video_id: str
    duration_s: float

@app.post("/api/v1/sessions")
def create_session(body: SessionCreate, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if body.video_id not in sessions: raise HTTPException(404, detail="Unknown video_id")
    if body.duration_s <= 0: raise HTTPException(400, detail="duration_s must be positive")
    sid = str(uuid.uuid4()); sessions[sid] = {"video_id":body.video_id, "timeline":Timeline(body.duration_s), "responses":[]}
    return {"session_id":sid, "timeline":sessions[sid]["timeline"].as_dict()}

@app.post("/api/v1/sessions/{session_id}/instructions")
def instruction(session_id: str, body: Instruction):
    state = sessions.get(session_id)
    if not state or not state.get("timeline"): raise HTTPException(404, detail="Unknown session")
    tl = state["timeline"]; op = parse_instruction(body.say, tl.duration)
    if op.get("type") == "undo": result = tl.undo()
    elif op.get("type") == "redo": result = tl.redo()
    elif op.get("type") == "render":
        result = {"status":"rejected","reason":"Rendering is not implemented in this starter MVP."}
    elif op.get("status"): result = op
    else:
        try: result = tl.apply(op)
        except Exception as e: result = {"status":"rejected","reason":str(e)}
    response = {**result, "timeline_hash":tl.as_dict()["timeline_hash"], "duration_s":round(tl.duration,3)}
    state["responses"].append(response)
    return response

@app.get("/api/v1/sessions/{session_id}/timeline")
def get_timeline(session_id: str):
    state=sessions.get(session_id)
    if not state or not state.get("timeline"): raise HTTPException(404, detail="Unknown session")
    return state["timeline"].as_dict()
