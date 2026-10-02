"""Algoritmos de análise real com tolerâncias e limites explícitos."""

from __future__ import annotations

from collections.abc import Callable
import math


def bisection(function: Callable[[float], float], left: float, right: float, *,
              tolerance: float = 1e-12, max_iterations: int = 1000) -> tuple[float, float]:
    if not all(math.isfinite(value) for value in (left, right, tolerance)) or left >= right or tolerance <= 0:
        raise ValueError("intervalo ou tolerância inválidos")
    f_left, f_right = function(left), function(right)
    if not math.isfinite(f_left) or not math.isfinite(f_right): raise ValueError("função não finita nos extremos")
    if f_left == 0: return left, 0.0
    if f_right == 0: return right, 0.0
    if f_left * f_right > 0: raise ValueError("extremos não isolam troca de sinal")
    for _ in range(max_iterations):
        middle = (left + right) / 2
        f_middle = function(middle)
        if not math.isfinite(f_middle): raise ValueError("função não finita durante iteração")
        if f_middle == 0 or (right - left) / 2 <= tolerance: return middle, (right - left) / 2
        if f_left * f_middle < 0: right, f_right = middle, f_middle
        else: left, f_left = middle, f_middle
    raise RuntimeError("bisseção não convergiu no orçamento")


def trapezoid(function: Callable[[float], float], left: float, right: float, intervals: int) -> float:
    if not isinstance(intervals, int) or not 1 <= intervals <= 10_000_000 or not left < right:
        raise ValueError("intervalo ou subdivisões inválidos")
    step = (right - left) / intervals
    values = [function(left + index * step) for index in range(intervals + 1)]
    if not all(math.isfinite(value) for value in values): raise ValueError("integrando não finito")
    return step * (values[0] / 2 + sum(values[1:-1]) + values[-1] / 2)


__all__ = ["bisection", "trapezoid"]
