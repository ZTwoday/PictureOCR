from storage.history import HistoryEntry, load_history, add_entry, delete_entry, clear_history


def _entry(eid, text="hello"):
    return HistoryEntry(id=eid, timestamp="2026-08-12T00:00:00", image_path="", text=text, engine="rapid")


def test_add_and_load_roundtrip(tmp_path):
    path = tmp_path / "history.json"
    add_entry(_entry("1"), str(path))
    entries = load_history(str(path))
    assert len(entries) == 1
    assert entries[0].id == "1"
    assert entries[0].text == "hello"


def test_add_trims_to_100(tmp_path):
    path = tmp_path / "history.json"
    for i in range(105):
        add_entry(_entry(f"id{i}"), str(path))
    assert len(load_history(str(path))) == 100


def test_delete_and_clear(tmp_path):
    path = tmp_path / "history.json"
    add_entry(_entry("1"), str(path))
    add_entry(_entry("2"), str(path))
    assert delete_entry("1", str(path)) is True
    assert delete_entry("nope", str(path)) is False
    assert [e.id for e in load_history(str(path))] == ["2"]
    clear_history(str(path))
    assert load_history(str(path)) == []
