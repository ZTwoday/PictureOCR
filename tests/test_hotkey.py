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
