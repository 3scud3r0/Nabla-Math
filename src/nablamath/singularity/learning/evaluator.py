"""Predeclared metric thresholds and baseline comparisons."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping


@dataclass(frozen=True)
class Evaluation:
    accepted: bool
    improvements: Mapping[str, float]
    failures: tuple[str, ...]


def evaluate_against_baseline(candidate: Mapping[str, float], baseline: Mapping[str, float],
                              minimum_improvement: Mapping[str, float]) -> Evaluation:
    if set(candidate) != set(baseline) or not set(minimum_improvement) <= set(candidate):
        raise ValueError("Métricas incompatíveis")
    improvements = {name: float(candidate[name]) - float(baseline[name]) for name in candidate}
    if any(not math.isfinite(value) for value in improvements.values()):
        raise ValueError("Métrica não finita")
    failures = tuple(name for name, threshold in minimum_improvement.items()
                     if improvements[name] < threshold)
    return Evaluation(not failures, improvements, failures)


__all__ = ["Evaluation", "evaluate_against_baseline"]
