"""Quantidades de informação para distribuições finitas."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Hashable, TypeVar


Event = TypeVar("Event", bound=Hashable)


def _distribution(values: Mapping[Event, float], name: str) -> dict[Event, float]:
    if not values:
        raise ValueError(f"{name} vazia")
    converted = {event: float(probability) for event, probability in values.items()}
    if any(not math.isfinite(value) or value < 0 for value in converted.values()):
        raise ValueError(f"{name} contém probabilidade inválida")
    if not math.isclose(sum(converted.values()), 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f"{name} não soma um")
    return converted


def entropy(distribution: Mapping[Event, float], base: float = 2.0) -> float:
    """Calcula a entropia de Shannon, ignorando termos de probabilidade zero."""
    values = _distribution(distribution, "distribuição")
    if not math.isfinite(base) or base <= 0 or base == 1:
        raise ValueError("base logarítmica inválida")
    return -sum(value * math.log(value, base) for value in values.values() if value)


def cross_entropy(
    distribution: Mapping[Event, float],
    reference: Mapping[Event, float],
    base: float = 2.0,
) -> float:
    """Calcula H(P,Q), retornando infinito quando Q zera suporte de P."""
    left = _distribution(distribution, "distribuição")
    right = _distribution(reference, "referência")
    if set(left) != set(right):
        raise ValueError("suportes incompatíveis")
    if not math.isfinite(base) or base <= 0 or base == 1:
        raise ValueError("base logarítmica inválida")
    if any(left[event] > 0 and right[event] == 0 for event in left):
        return math.inf
    return -sum(left[event] * math.log(right[event], base) for event in left if left[event])


def relative_entropy(
    distribution: Mapping[Event, float],
    reference: Mapping[Event, float],
    base: float = 2.0,
) -> float:
    """Calcula a divergência de Kullback-Leibler D(P||Q)."""
    cross = cross_entropy(distribution, reference, base)
    if math.isinf(cross):
        return cross
    return cross - entropy(distribution, base)


def joint_entropy(
    distribution: Mapping[tuple[Event, Event], float], base: float = 2.0
) -> float:
    return entropy(distribution, base)


def mutual_information(
    distribution: Mapping[tuple[Event, Event], float], base: float = 2.0
) -> float:
    """Calcula I(X;Y) a partir de uma distribuição conjunta finita."""
    joint = _distribution(distribution, "distribuição conjunta")
    left: dict[Event, float] = {}
    right: dict[Event, float] = {}
    for (first, second), probability in joint.items():
        left[first] = left.get(first, 0.0) + probability
        right[second] = right.get(second, 0.0) + probability
    total = 0.0
    for (first, second), probability in joint.items():
        if probability:
            total += probability * math.log(probability / (left[first] * right[second]), base)
    return total


__all__ = [
    "cross_entropy",
    "entropy",
    "joint_entropy",
    "mutual_information",
    "relative_entropy",
]
