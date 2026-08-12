import json
import os

DEFAULT_CONFIG = {"hotkey": "Ctrl+Alt+A", "default_engine": "rapid"}


def data_dir() -> str:
    return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), ".ocr_app")


def default_config_path() -> str:
    return os.path.join(data_dir(), "config.json")


def load_config(path: str | None = None) -> dict:
    path = path or default_config_path()
    config = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass
    return config


def save_config(config: dict, path: str | None = None) -> None:
    path = path or default_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
