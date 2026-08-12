import json
import os

MAX_ENTRIES = 100


class HistoryEntry:
    def __init__(self, id: str, timestamp: str, image_path: str, text: str, engine: str):
        self.id = id
        self.timestamp = timestamp
        self.image_path = image_path
        self.text = text
        self.engine = engine

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        return cls(d["id"], d["timestamp"], d.get("image_path", ""), d.get("text", ""), d.get("engine", ""))

    def to_dict(self) -> dict:
        return {"id": self.id, "timestamp": self.timestamp, "image_path": self.image_path,
                "text": self.text, "engine": self.engine}


def default_history_path() -> str:
    from core.config import data_dir
    return os.path.join(data_dir(), "history.json")


def load_history(path: str | None = None) -> list[HistoryEntry]:
    path = path or default_history_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return [HistoryEntry.from_dict(d) for d in json.load(f)]
    except (json.JSONDecodeError, OSError, KeyError):
        return []


def _write(path: str, entries: list[HistoryEntry]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in entries], f, ensure_ascii=False, indent=2)


def add_entry(entry: HistoryEntry, path: str | None = None) -> None:
    path = path or default_history_path()
    entries = load_history(path)
    entries.insert(0, entry)
    _write(path, entries[:MAX_ENTRIES])


def delete_entry(entry_id: str, path: str | None = None) -> bool:
    path = path or default_history_path()
    entries = load_history(path)
    remaining = [e for e in entries if e.id != entry_id]
    if len(remaining) == len(entries):
        return False
    _write(path, remaining)
    return True


def clear_history(path: str | None = None) -> None:
    path = path or default_history_path()
    _write(path, [])
