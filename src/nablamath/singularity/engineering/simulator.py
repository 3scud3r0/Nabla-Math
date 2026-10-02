"""Restricted deterministic state-transition simulation."""

from __future__ import annotations

from typing import Callable, TypeVar

State = TypeVar("State")


def simulate(initial: State, transition: Callable[[State, int], State], steps: int,
             invariant: Callable[[State], bool]) -> tuple[State, ...]:
    if type(steps) is not int or not 0 <= steps <= 1_000_000:
        raise ValueError("steps fora do limite")
    history = [initial]
    if not invariant(initial):
        raise ArithmeticError("Estado inicial viola invariante")
    for index in range(steps):
        state = transition(history[-1], index)
        if not invariant(state):
            raise ArithmeticError(f"Invariante violado no passo {index + 1}")
        history.append(state)
    return tuple(history)


__all__ = ["simulate"]
