# IncuBrix Prompt-Based Video Editing Engine — Starter MVP

> **Status: incomplete starter scaffold, not assessment-ready.** It demonstrates deterministic source-interval timeline data and a small API. It does not yet meet all assessment must-haves.

## Run locally
1. Install Python 3.12+ and Docker.
2. `docker compose up --build`
3. Open `http://localhost:8000/docs`
4. Check `http://localhost:8000/health`

## API flow
1. `POST /api/v1/videos` with an MP4/MOV multipart upload.
2. `POST /api/v1/sessions` with the returned `video_id` and the video duration in seconds.
3. `POST /api/v1/sessions/{session_id}/instructions` with `{"say":"Cut the first 30 seconds"}`.
4. `GET /api/v1/sessions/{session_id}/timeline`.

## Implemented in this scaffold
- Original upload is saved separately and hashed.
- Timeline edits reference source intervals instead of only output clock positions.
- Deterministic timeline hash.
- Basic cut/keep/caption/speed/mute timeline operations (with documented limitations).
- Undo/redo for timeline operations.
- Basic instruction parser and clarification response for vague requests.
- Health/readiness endpoints and small unit test suite.

## Known gaps — do not claim these are complete
- Word-level transcription and speaker/confidence fields are not implemented.
- FFmpeg/ffprobe rendering is not implemented; render currently returns a rejection.
- Captions are stored as data but not rendered or fully content-aligned.
- Session runner currently accepts JSON rather than the required YAML-like format and assumes a video/session is already registered.
- No persistent database/job queue, idempotency store, object storage, OpenAPI file, 15-session test pack, or live deployment.
- No robust semantic search or multi-speaker handling.
- Speed operation is restricted in this MVP.
- API errors and asynchronous jobs do not yet fully satisfy the Integration Standard.

## Test
`pytest -q`

## Before submission
Do not mark requirements Yes unless you have evidence. The assessment explicitly disqualifies false claims. Complete the must-haves, capture real test evidence, and disclose all tools/models/libraries in `AI_USE.md` and `SOURCES.md`.
