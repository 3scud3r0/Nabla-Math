"""Checkpoint local idempotente para não repetir tarefas concluídas."""

import json
from pathlib import Path


class Checkpoint:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._items = json.loads(self.path.read_text()) if self.path.is_file() else {}

    def done(self, task_id: str, result_id: str) -> None:
        if not task_id or not result_id:
            raise ValueError("ids obrigatórios")
        self._items[task_id] = result_id
        self.path.write_text(json.dumps(self._items, sort_keys=True) + "\n", encoding="utf-8")

    def result(self, task_id: str) -> str | None:
        return self._items.get(task_id)
