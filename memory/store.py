"""JSONL memory store for previous research runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonMemoryStore:
    def __init__(self, path: str | Path = "memory/runs.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 5) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows = self.path.read_text(encoding="utf-8").splitlines()
        return [json.loads(row) for row in rows[-limit:] if row.strip()]
