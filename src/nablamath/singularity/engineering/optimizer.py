"""Deterministic Pareto selection for measured candidate implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Candidate:
    identifier: str
    metrics: Mapping[str, float]


def pareto_front(candidates: tuple[Candidate, ...], minimize: frozenset[str]) -> tuple[Candidate, ...]:
    if not candidates:
        return ()
    keys = set(candidates[0].metrics)
    if any(set(candidate.metrics) != keys for candidate in candidates) or not minimize <= keys:
        raise ValueError("Candidatos usam métricas incompatíveis")

    def value(candidate: Candidate, key: str) -> float:
        return candidate.metrics[key] if key in minimize else -candidate.metrics[key]

    result = []
    for candidate in candidates:
        dominated = any(
            other != candidate
            and all(value(other, key) <= value(candidate, key) for key in keys)
            and any(value(other, key) < value(candidate, key) for key in keys)
            for other in candidates
        )
        if not dominated:
            result.append(candidate)
    return tuple(sorted(result, key=lambda item: item.identifier))


__all__ = ["Candidate", "pareto_front"]
