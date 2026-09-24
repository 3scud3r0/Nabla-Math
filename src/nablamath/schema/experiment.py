"""Experimento reprodutível com semente e limite de tentativas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Experiment:
    name: str
    algorithm_version: str
    seed: int
    max_trials: int

    def __post_init__(self) -> None:
        if not self.name or not self.algorithm_version or not 1 <= self.max_trials <= 10_000_000:
            raise ValueError("Experimento requer nome, versão e orçamento positivo")
