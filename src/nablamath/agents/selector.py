"""Seleção transparente de propostas por prioridade, novidade estrutural e custo."""

from __future__ import annotations

from dataclasses import dataclass
from ..dataset.deduplicate import normalized_expression


@dataclass(frozen=True)
class Candidate:
    identifier: str
    expression: str
    relevance: float = 0.0
    estimated_cost: float = 1.0

    def score(self, known: set[str]) -> float:
        if not 0 <= self.relevance <= 1 or self.estimated_cost <= 0:
            raise ValueError("relevância/custo fora do domínio")
        novelty = 0.0 if normalized_expression(self.expression) in known else 1.0
        return (self.relevance + novelty) / self.estimated_cost


def select(candidates: list[Candidate], *, known: set[str] | None = None,
           limit: int = 10) -> list[Candidate]:
    if limit < 1:
        raise ValueError("limit deve ser positivo")
    known = known or set()
    return sorted(candidates, key=lambda c: (-c.score(known), c.identifier))[:limit]


__all__ = ["Candidate", "select"]
