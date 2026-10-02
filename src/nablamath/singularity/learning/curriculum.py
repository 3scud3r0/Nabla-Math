"""Select the next bounded task from calibrated difficulty and learning value."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CurriculumItem:
    identifier: str
    difficulty: float
    expected_information_gain: float
    prerequisites: tuple[str, ...] = ()


def select_curriculum(items: tuple[CurriculumItem, ...], completed: set[str], limit: int) -> tuple[CurriculumItem, ...]:
    if limit < 1:
        raise ValueError("limit deve ser positivo")
    eligible = [item for item in items if item.identifier not in completed
                and set(item.prerequisites) <= completed]
    if any(not math.isfinite(item.difficulty + item.expected_information_gain) for item in eligible):
        raise ValueError("Currículo contém valor não finito")
    return tuple(sorted(eligible, key=lambda item: (
        -(item.expected_information_gain / (1 + max(0.0, item.difficulty))), item.identifier
    ))[:limit])


__all__ = ["CurriculumItem", "select_curriculum"]
