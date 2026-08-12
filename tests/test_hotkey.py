from core.hotkey import parse_hotkey, MOD_CONTROL, MOD_ALT, MOD_SHIFT


def test_parse_hotkey_ctrl_alt_a():
    mods, vk = parse_hotkey("Ctrl+Alt+A")
    assert mods & MOD_CONTROL
    assert mods & MOD_ALT
    assert vk == 0x41


def test_parse_hotkey_ctrl_shift_b():
    mods, vk = parse_hotkey("Ctrl+Shift+B")
    assert mods & MOD_CONTROL
    assert mods & MOD_SHIFT
    assert vk == 0x42


def test_unregister_removes_filter_and_state(app, monkeypatch):
    from PySide6.QtGui import QGuiApplication
    from core.hotkey import GlobalHotkey

    gh = GlobalHotkey()
    calls = []
    monkeypatch.setattr(gh._user32, "RegisterHotKey",
                        lambda hwnd, id_, mods, vk: calls.append(("reg", id_)) or 1)
    monkeypatch.setattr(gh._user32, "UnregisterHotKey",
                        lambda hwnd, id_: calls.append(("unreg", id_)) or 1)

    ok = gh.register(0, "Ctrl+Alt+A", lambda: None)
    assert ok
    assert gh._filter is not None
    assert QGuiApplication.instance() is not None
    assert gh._hwnd == 0

    gh.unregister()

    assert gh._hwnd is None
    assert gh._filter is None
    assert ("reg", gh._id) in calls
    assert ("unreg", gh._id) in calls
