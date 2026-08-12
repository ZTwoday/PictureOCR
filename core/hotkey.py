import ctypes
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, QObject

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312

_MOD_NAMES = {"ctrl": MOD_CONTROL, "alt": MOD_ALT, "shift": MOD_SHIFT}


def parse_hotkey(spec: str) -> tuple[int, int]:
    parts = [p.strip().lower() for p in spec.split("+")]
    key = parts[-1]
    mods = 0
    for p in parts[:-1]:
        if p in _MOD_NAMES:
            mods |= _MOD_NAMES[p]
    vk = ord(key.upper()) if len(key) == 1 else ord("A")
    return mods, vk


class HotkeyEventFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def nativeEventFilter(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                self.callback()
                return True, 0
        return False, 0


class GlobalHotkey(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user32 = ctypes.windll.user32
        self._user32.RegisterHotKey.restype = wintypes.BOOL
        self._user32.RegisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.UINT,
        ]
        self._user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        self._filter = None
        self._hwnd = None
        self._id = 1

    def register(self, hwnd: int, spec: str, callback) -> bool:
        mods, vk = parse_hotkey(spec)
        ok = self._user32.RegisterHotKey(hwnd, self._id, mods | MOD_NOREPEAT, vk)
        if not ok:
            return False
        self._filter = HotkeyEventFilter(callback)
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.instance().installNativeEventFilter(self._filter)
        self._hwnd = hwnd
        return True

    def unregister(self):
        if self._hwnd is not None:
            self._user32.UnregisterHotKey(self._hwnd, self._id)
        self._hwnd = None
