"""Órbitas de sistemas dinâmicos discretos determinísticos."""

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Orbit(Generic[T]):
    values: tuple[T, ...]
    transient_length: int | None
    period: int | None


def iterate(function: Callable[[T], T], initial: T, steps: int) -> tuple[T, ...]:
    if not 0 <= steps <= 10_000_000: raise ValueError("quantidade de passos fora do limite")
    values = [initial]
    for _ in range(steps): values.append(function(values[-1]))
    return tuple(values)


def detect_cycle(function: Callable[[T], T], initial: T, *, max_steps: int = 100_000) -> Orbit[T]:
    if not 1 <= max_steps <= 10_000_000: raise ValueError("limite de passos inválido")
    seen: dict[T, int] = {}; values = []; current = initial
    for _ in range(max_steps):
        try: previous = seen.get(current)
        except TypeError as exc: raise ValueError("estados precisam ser hashable") from exc
        if previous is not None:
            return Orbit(tuple(values), previous, len(values) - previous)
        seen[current] = len(values); values.append(current); current = function(current)
    return Orbit(tuple(values), None, None)


__all__ = ["Orbit", "detect_cycle", "iterate"]
