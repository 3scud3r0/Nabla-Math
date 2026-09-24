"""Grafo local determinístico de transformações registradas, sem eval ou shell."""

from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class Task:
    name: str
    dependencies: tuple[str, ...]
    operation: Callable[[Mapping[str, object]], object]


class Pipeline:
    def __init__(self, tasks: list[Task]):
        if len({task.name for task in tasks}) != len(tasks):
            raise ValueError("Nomes de tarefas duplicados")
        self.tasks = {task.name: task for task in tasks}

    def run(self, target: str) -> dict[str, object]:
        outputs: dict[str, object] = {}
        active: set[str] = set()

        def visit(name: str) -> None:
            if name in outputs:
                return
            if name in active:
                raise ValueError("Ciclo detectado no DAG")
            if name not in self.tasks:
                raise ValueError(f"Dependência desconhecida: {name}")
            active.add(name)
            task = self.tasks[name]
            for dependency in task.dependencies:
                visit(dependency)
            value = task.operation({d: outputs[d] for d in task.dependencies})
            outputs[name] = value
            active.remove(name)

        visit(target)
        return outputs
