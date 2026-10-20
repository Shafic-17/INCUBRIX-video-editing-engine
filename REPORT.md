# Engineering Report — Prompt-Based Video Editing Engine

## Objective
Build an editing engine that converts plain-language instructions into deterministic, reversible operations on an editable video timeline. The design principle is that edits should remain attached to source content rather than fixed output clock positions.

## Approach
The starter implementation stores timeline segments as intervals in the original media (`source_start`, `source_end`) and maps current timeline ranges back to source intervals. The original upload is stored separately and hashed. Each operation stores before/after snapshots to support undo/redo. A SHA-256 hash of a canonical JSON representation is used to check deterministic timeline state.

A small rule-based parser maps a limited set of exact phrases to structured operations. This keeps timeline mutation in ordinary deterministic code rather than delegating state changes to an AI model.

## Current status
This is an initial scaffold, not a complete assessment solution. Basic API endpoints, source-interval timeline operations, undo/redo, and unit tests are present. Word-level transcription, accurate media rendering, robust time policy, speaker handling, and full integration requirements remain incomplete.

## Measurements
Do not report latency, audio/video sync, word clipping, transcription cost, or 100% end-to-end determinism until measured with real media and repeatable test runs. Record actual measurements and link the test artifacts here.

## Risks and next steps
1. Implement ffprobe metadata extraction and FFmpeg rendering with frame-accurate duration checks.
2. Add transcription adapter returning word-level timestamps, speaker labels, and confidence.
3. Define and validate a JSON Schema for the timeline and content-anchored caption behavior.
4. Implement deterministic parsing for the required command set and ambiguity/contradiction checks.
5. Add idempotency, background jobs, structured logs, output manifest, OpenAPI 3.1, and MinIO-compatible storage.
6. Run at least 15 scripted sessions, preserve failures, and report evidence honestly.
