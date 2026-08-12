from ui.history_window import HistoryWindow


def test_refresh_populates_list(app, monkeypatch, tmp_path):
    from storage.history import HistoryEntry, add_entry, default_history_path
    path = tmp_path / "history.json"
    add_entry(HistoryEntry(id="1", timestamp="2026-08-12", image_path="", text="第一行文字", engine="rapid"), str(path))

    window = HistoryWindow()
    monkeypatch.setattr("ui.history_window.default_history_path", lambda: str(path))
    window.refresh()
    assert window.list_widget.count() == 1
    assert "第一行" in window.list_widget.item(0).text()
