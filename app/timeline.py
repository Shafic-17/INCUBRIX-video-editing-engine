"""Deterministic content-anchored timeline primitives for the IncuBrix assessment MVP."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import hashlib, json, copy

@dataclass
class Segment:
    id: str
    source_start: float
    source_end: float
    speed: float = 1.0
    muted: bool = False

    @property
    def duration(self) -> float:
        return max(0.0, (self.source_end - self.source_start) / self.speed)

class Timeline:
    """Timeline references original-source intervals, so edits do not mutate the source."""
    def __init__(self, duration: float):
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.source_duration = float(duration)
        self.segments = [Segment("seg-0", 0.0, float(duration))]
        self.captions: list[dict[str, Any]] = []
        self.history: list[dict[str, Any]] = []
        self.redo_stack: list[dict[str, Any]] = []
        self._next_id = 1

    @property
    def duration(self) -> float:
        return sum(s.duration for s in self.segments)

    def snapshot(self):
        return {"segments": [asdict(s) for s in self.segments],
                "captions": copy.deepcopy(self.captions), "next_id": self._next_id}

    def restore_snapshot(self, snap):
        self.segments = [Segment(**s) for s in snap["segments"]]
        self.captions = copy.deepcopy(snap["captions"])
        self._next_id = snap["next_id"]

    def apply(self, op: dict):
        before = self.snapshot()
        kind = op.get("type")
        if kind == "cut":
            start, end = float(op["start"]), float(op["end"])
            if start < 0 or end <= start or end > self.duration:
                raise ValueError("Cut range is outside the current timeline")
            self._slice_keep([(0, start), (end, self.duration)])
        elif kind == "keep":
            start, end = float(op["start"]), float(op["end"])
            if start < 0 or end <= start or end > self.duration:
                raise ValueError("Keep range is outside the current timeline")
            self._slice_keep([(start, end)])
        elif kind == "speed":
            start, end, factor = float(op["start"]), float(op["end"]), float(op["factor"])
            if start < 0 or end <= start or end > self.duration or not (0.25 <= factor <= 4):
                raise ValueError("Invalid speed range/factor (supported range: 0.25x–4x)")
            # MVP only supports speed changes that align with whole segment boundaries.
            if start != 0 or end != self.duration or len(self.segments) != 1:
                raise ValueError("MVP speed operation currently requires the whole current timeline")
            self.segments[0].speed = factor
        elif kind == "caption":
            text = str(op.get("text", "")).strip()
            if not text: raise ValueError("Caption text cannot be empty")
            # Anchor to original-source time/content, not rendered clock time.
            self.captions.append({"id": f"cap-{self._next_id}", "text": text,
                                  "source_start": float(op.get("source_start", 0)),
                                  "source_end": float(op.get("source_end", min(2, self.source_duration))),
                                  "style": {"color": op.get("color", "white"), "size": int(op.get("size", 32))}})
            self._next_id += 1
        elif kind == "mute":
            start, end = float(op["start"]), float(op["end"])
            if start < 0 or end <= start or end > self.duration:
                raise ValueError("Mute range is outside the current timeline")
            # Mark whole intersecting segments muted; conservative MVP behavior.
            hit = False
            for s in self.segments:
                if s.source_start < end and s.source_end > start:
                    s.muted = True; hit = True
            if not hit: raise ValueError("No segment overlaps the requested mute range")
        else:
            raise ValueError(f"Unsupported operation: {kind}")
        self.history.append({"operation": copy.deepcopy(op), "before": before, "after": self.snapshot()})
        self.redo_stack.clear()
        return {"status": "applied", "operation": op, "duration_before_s": round(sum(
            (x["source_end"]-x["source_start"])/x["speed"] for x in before["segments"]), 3),
            "duration_after_s": round(self.duration, 3)}

    def _slice_keep(self, ranges):
        # Map current-timeline intervals onto source intervals; preserves content identity.
        new_segments = []
        cursor = 0.0
        for seg in self.segments:
            seg_dur = seg.duration
            for a, b in ranges:
                lo, hi = max(a, cursor), min(b, cursor + seg_dur)
                if hi > lo:
                    src_lo = seg.source_start + (lo - cursor) * seg.speed
                    src_hi = seg.source_start + (hi - cursor) * seg.speed
                    new_segments.append(Segment(f"seg-{self._next_id}", src_lo, src_hi, seg.speed, seg.muted))
                    self._next_id += 1
            cursor += seg_dur
        self.segments = new_segments

    def undo(self):
        if not self.history: return {"status":"rejected", "reason":"Nothing to undo"}
        item = self.history.pop()
        self.redo_stack.append(item)
        self.restore_snapshot(item["before"])
        return {"status":"applied", "operation":{"type":"undo"}, "duration_after_s":round(self.duration,3)}

    def redo(self):
        if not self.redo_stack: return {"status":"rejected", "reason":"Nothing to redo"}
        item = self.redo_stack.pop()
        self.restore_snapshot(item["after"])
        self.history.append(item)
        return {"status":"applied", "operation":{"type":"redo"}, "duration_after_s":round(self.duration,3)}

    def as_dict(self):
        data = {"source_duration_s": self.source_duration, "duration_s": round(self.duration, 6),
                "segments": [asdict(s) for s in self.segments], "captions": self.captions}
        data["timeline_hash"] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return data
