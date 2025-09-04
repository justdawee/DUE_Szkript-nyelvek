from pathlib import Path
from datetime import datetime
import json

class ABHistory:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.items = []
        if self.path.exists():
            try:
                self.items = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.items = []

    def add(self, action: str, text: str, image_path: str, ts: str):
        self.items.append({"action": action, "text": text, "image_path": image_path, "ts": ts})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.items, ensure_ascii=False, indent=2), encoding="utf-8")

    def recent(self, n: int = 20):
        return list(reversed(self.items[-n:]))

def ab_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")
