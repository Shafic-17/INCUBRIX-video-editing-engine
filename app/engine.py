"""Small rule-based instruction parser. LLM adapters can be added without moving timeline logic."""
import re

def parse_instruction(text: str, duration: float):
    s = text.strip().lower()
    if s in ("undo", "undo the previous edit"): return {"type":"undo"}
    if s == "redo": return {"type":"redo"}
    if s in ("render", "export"): return {"type":"render"}
    m = re.fullmatch(r"cut the first (\d+(?:\.\d+)?) seconds?", s)
    if m: return {"type":"cut", "start":0, "end":float(m.group(1))}
    m = re.fullmatch(r"(?:cut|remove) (\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", s)
    if m: return {"type":"cut", "start":float(m.group(1)), "end":float(m.group(2))}
    m = re.fullmatch(r"speed up (?:the )?whole video by (\d+(?:\.\d+)?)x", s)
    if m: return {"type":"speed", "start":0, "end:":duration, "end":duration, "factor":float(m.group(1))}
    m = re.fullmatch(r"add a caption ['\"](.+?)['\"]", text.strip(), re.I)
    if m: return {"type":"caption", "text":m.group(1), "source_start":0, "source_end":min(2,duration)}
    if "pricing" in s or "boring" in s or "that part" in s:
        return {"status":"needs_clarification", "question":"Which section do you mean? Provide a time range (for example, 60-75).", "options":["Enter a time range","Cancel"]}
    return {"status":"rejected", "reason":"Instruction not supported by the MVP parser. Try a documented command."}
