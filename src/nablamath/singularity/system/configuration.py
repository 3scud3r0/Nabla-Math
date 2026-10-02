"""Immutable safety and resource configuration for research cycles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LabConfiguration:
    max_tasks: int = 256
    max_hypotheses: int = 64
    max_iterations: int = 16
    max_memory_records: int = 10_000
    allow_network: bool = False
    allow_generated_code_execution: bool = False
    seed: int = 0

    def __post_init__(self) -> None:
        for name in ("max_tasks", "max_hypotheses", "max_iterations", "max_memory_records"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f"{name} deve ser inteiro positivo")
        if self.allow_generated_code_execution:
            raise ValueError("Execução de código gerado não é suportada por este laboratório")


__all__ = ["LabConfiguration"]
