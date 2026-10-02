"""Contratos declarativos de tarefa; não executam código nem abrem rede."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from ..network.objects import OBJECT_TYPES
from .resources import ResourceBudget

TASK_TYPES = frozenset({"solve", "verify", "criticize", "formalize", "find_counterexample", "deduplicate"})


@dataclass(frozen=True)
class BoundedTask:
    task_type: str
    input_ids: tuple[str, ...]
    accepted_output_types: tuple[str, ...]
    budget: ResourceBudget

    def __post_init__(self) -> None:
        if self.task_type not in TASK_TYPES:
            raise ValueError("tipo de tarefa não suportado")
        if not self.input_ids or tuple(sorted(set(self.input_ids))) != self.input_ids:
            raise ValueError("entradas devem estar ordenadas, sem duplicatas e não vazias")
        if any(len(item) != 64 or any(c not in "0123456789abcdef" for c in item) for item in self.input_ids):
            raise ValueError("entrada não é um SHA-256")
        if not self.accepted_output_types or tuple(sorted(set(self.accepted_output_types))) != self.accepted_output_types:
            raise ValueError("saídas devem estar ordenadas, sem duplicatas e não vazias")
        if any(item not in OBJECT_TYPES for item in self.accepted_output_types):
            raise ValueError("tipo de saída não suportado")

    def to_data(self) -> dict[str, object]:
        return {"task_type": self.task_type, "input_ids": list(self.input_ids),
                "accepted_output_types": list(self.accepted_output_types),
                "budget": asdict(self.budget)}

    def accepted_by(self, local_budget: ResourceBudget) -> bool:
        return local_budget.permits(self.budget)


__all__ = ["BoundedTask", "TASK_TYPES"]
