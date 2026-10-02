"""Deterministic dependency-aware plans with cycle rejection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TaskKind = Literal["research", "mathematics", "science", "code", "test", "critique", "evaluate"]


@dataclass(frozen=True)
class Task:
    identifier: str
    kind: TaskKind
    objective: str
    dependencies: tuple[str, ...] = ()
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.identifier or not self.objective.strip():
            raise ValueError("Tarefa exige identificador e objetivo")
        if self.identifier in self.dependencies:
            raise ValueError("Tarefa não pode depender de si mesma")


class Plan:
    def __init__(self, tasks: tuple[Task, ...], *, task_limit: int = 256) -> None:
        if len(tasks) > task_limit:
            raise ValueError("Plano excede limite de tarefas")
        self.tasks = tasks
        mapping = {task.identifier: task for task in tasks}
        if len(mapping) != len(tasks):
            raise ValueError("IDs de tarefa duplicados")
        if any(set(task.dependencies) - set(mapping) for task in tasks):
            raise ValueError("Plano contém dependência ausente")
        self._mapping = mapping
        self.order = self._topological_order()

    def _topological_order(self) -> tuple[str, ...]:
        pending = {key: set(task.dependencies) for key, task in self._mapping.items()}
        order: list[str] = []
        while pending:
            ready = sorted((key for key, deps in pending.items() if not deps),
                           key=lambda key: (-self._mapping[key].priority, key))
            if not ready:
                raise ValueError("Plano contém ciclo")
            for key in ready:
                order.append(key)
                del pending[key]
            for deps in pending.values():
                deps.difference_update(ready)
        return tuple(order)

    def ready(self, completed: set[str]) -> tuple[Task, ...]:
        return tuple(self._mapping[key] for key in self.order
                     if key not in completed and set(self._mapping[key].dependencies) <= completed)


__all__ = ["Plan", "Task", "TaskKind"]
