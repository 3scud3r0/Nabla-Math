"""Worker opt-in que executa somente a tarefa declarativa recebida."""

from nablamath.research import calculate


class Worker:
    def __init__(self, participant_id: str, *, max_tasks: int = 10):
        if not participant_id or not 1 <= max_tasks <= 10_000:
            raise ValueError("identidade ou cota inválida")
        self.participant_id, self.max_tasks, self.completed = participant_id, max_tasks, 0

    def execute(self, task: dict) -> str:
        if self.completed >= self.max_tasks:
            raise RuntimeError("cota do worker esgotada")
        result = calculate(task["expression"], task["values"])
        self.completed += 1
        return result.content_id
