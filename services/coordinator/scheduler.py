"""Agendador que delega a fila SQLite e rejeita parâmetros fora das cotas."""

from pathlib import Path

from nablamath.coordination.local import LocalCoordinator


class Scheduler:
    def __init__(self, database: str | Path):
        self.queue = LocalCoordinator(Path(database))

    def add(self, expression: str, values: dict) -> str:
        return self.queue.add(expression, values)

    def lease(self, participant: str, seconds: int = 60) -> dict | None:
        return self.queue.lease(participant, seconds)

    def submit(self, participant: str, task_id: str, result_id: str) -> str:
        return self.queue.submit(participant, task_id, result_id)

    def status(self, task_id: str) -> str | None:
        return self.queue.status(task_id)
