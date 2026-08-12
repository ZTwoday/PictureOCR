import json
from core.config import DEFAULT_CONFIG, load_config, save_config


def test_load_config_returns_defaults_when_missing(tmp_path):
    path = tmp_path / "config.json"
    config = load_config(str(path))
    assert config == DEFAULT_CONFIG


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "config.json"
    save_config({"hotkey": "Ctrl+Shift+R", "default_engine": "baidu"}, str(path))
    assert json.loads(path.read_text(encoding="utf-8"))["default_engine"] == "baidu"
    assert load_config(str(path))["hotkey"] == "Ctrl+Shift+R"
