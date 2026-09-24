"""Coordenador SQLite local para tarefas racionais; sem serviço de rede/identidade."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import time

from ..research import calculate


class LocalCoordinator:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, expression TEXT NOT NULL, values_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', result_id TEXT);
            CREATE TABLE IF NOT EXISTS leases (
                task_id TEXT NOT NULL, worker TEXT NOT NULL, expires REAL NOT NULL,
                result_id TEXT, PRIMARY KEY(task_id,worker));
            """)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=30)

    def add(self, expression: str, values: dict[str, str | int]) -> str:
        calculated = calculate(expression, values)  # valida antes de oferecer tarefa
        normalized = {k: str(v) for k,v in calculated.values.items()}
        canonical = json.dumps([expression, normalized], sort_keys=True, separators=(",", ":"))
        identifier = hashlib.sha256(canonical.encode()).hexdigest()
        with self._connect() as db:
            db.execute("INSERT OR IGNORE INTO tasks (task_id,expression,values_json) VALUES (?,?,?)",
                       (identifier, expression, json.dumps(normalized, sort_keys=True)))
        return identifier

    def lease(self, worker: str, seconds: int = 60) -> dict | None:
        if not worker or len(worker) > 128 or not 1 <= seconds <= 3600:
            raise ValueError("Trabalhador ou prazo inválidos")
        now = time.time()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            tasks = db.execute("SELECT task_id,expression,values_json FROM tasks WHERE status='pending' ORDER BY task_id")
            for task_id, expression, values_json in tasks:
                occupied = db.execute("SELECT worker,expires,result_id FROM leases WHERE task_id=?", (task_id,)).fetchall()
                if any(name == worker for name, _, _ in occupied):
                    continue
                if sum(result is not None or expires > now for _, expires, result in occupied) >= 2:
                    continue
                db.execute("INSERT INTO leases VALUES (?,?,?,NULL)", (task_id,worker,now+seconds))
                return {"task_id": task_id, "expression": expression, "values": json.loads(values_json),
                        "lease_expires_unix": now+seconds}
        return None

    def submit(self, worker: str, task_id: str, result_id: str) -> str:
        """Reexecuta o cálculo localmente; aceita consenso só de duas IDs de worker distintas."""
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            task = db.execute("SELECT expression,values_json,status FROM tasks WHERE task_id=?",
                              (task_id,)).fetchone()
            lease = db.execute("SELECT expires,result_id FROM leases WHERE task_id=? AND worker=?",
                               (task_id,worker)).fetchone()
            if task is None or lease is None or task[2] != "pending" or lease[1] is not None or lease[0] <= time.time():
                raise ValueError("Tarefa ou lease inválido/expirado")
            expected = calculate(task[0], json.loads(task[1])).content_id
            if result_id != expected:
                raise ValueError("Resultado do trabalhador não passou na reexecução")
            db.execute("UPDATE leases SET result_id=? WHERE task_id=? AND worker=?",
                       (result_id,task_id,worker))
            agreed = db.execute("SELECT COUNT(*) FROM leases WHERE task_id=? AND result_id=?",
                                (task_id,result_id)).fetchone()[0]
            if agreed >= 2:
                db.execute("UPDATE tasks SET status='verified',result_id=? WHERE task_id=?",
                           (result_id,task_id))
                return "verified"
            return "awaiting_second_worker"

    def status(self, task_id: str) -> str | None:
        with self._connect() as db:
            row = db.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return row[0] if row else None
