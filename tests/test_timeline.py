from app.timeline import Timeline

def test_cut_preserves_source_content_and_duration():
    t=Timeline(100)
    t.apply({"type":"cut","start":0,"end":30})
    assert t.duration == 70
    assert t.segments[0].source_start == 30

def test_undo_restores_previous_timeline():
    t=Timeline(100); t.apply({"type":"cut","start":0,"end":30})
    t.undo()
    assert t.duration == 100

def test_redo_reapplies_edit():
    t=Timeline(100); t.apply({"type":"cut","start":0,"end":30}); t.undo(); t.redo()
    assert t.duration == 70

def test_same_timeline_hash_is_deterministic():
    a=Timeline(60).as_dict(); b=Timeline(60).as_dict()
    assert a["timeline_hash"] == b["timeline_hash"]
