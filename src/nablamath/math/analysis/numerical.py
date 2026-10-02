"""Métodos numéricos escalares com contratos explícitos de erro e domínio."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass


ScalarFunction = Callable[[float], float]


def _finite(value: float, name: str) -> float:
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{name} deve ser finito")
    return converted


def derivative(
    function: ScalarFunction,
    point: float,
    step: float = 1e-5,
    *,
    method: str = "central",
) -> float:
    """Aproxima a primeira derivada por diferenças finitas.

    ``central`` possui erro de truncamento quadrático; os métodos laterais
    possuem erro linear e são úteis nas fronteiras de um domínio.
    """
    point = _finite(point, "ponto")
    step = _finite(step, "passo")
    if step <= 0:
        raise ValueError("passo deve ser positivo")
    if method == "central":
        result = (function(point + step) - function(point - step)) / (2 * step)
    elif method == "forward":
        result = (function(point + step) - function(point)) / step
    elif method == "backward":
        result = (function(point) - function(point - step)) / step
    else:
        raise ValueError("método deve ser central, forward ou backward")
    return _finite(result, "derivada")


def second_derivative(function: ScalarFunction, point: float, step: float = 1e-4) -> float:
    """Aproxima a segunda derivada com diferença central de três pontos."""
    point = _finite(point, "ponto")
    step = _finite(step, "passo")
    if step <= 0:
        raise ValueError("passo deve ser positivo")
    result = (function(point + step) - 2 * function(point) + function(point - step)) / step**2
    return _finite(result, "segunda derivada")


def simpson(function: ScalarFunction, start: float, end: float, intervals: int = 100) -> float:
    """Integra com a regra composta de Simpson em número par de intervalos."""
    start = _finite(start, "início")
    end = _finite(end, "fim")
    if start == end:
        return 0.0
    if not isinstance(intervals, int) or not 2 <= intervals <= 10_000_000 or intervals % 2:
        raise ValueError("intervals deve ser um inteiro par entre 2 e 10.000.000")
    step = (end - start) / intervals
    total = _finite(function(start), "valor da função") + _finite(function(end), "valor da função")
    for index in range(1, intervals):
        weight = 4 if index % 2 else 2
        total += weight * _finite(function(start + index * step), "valor da função")
    return _finite(total * step / 3, "integral")


@dataclass(frozen=True)
class RootResult:
    """Resultado auditável de uma busca iterativa por raiz."""

    root: float
    residual: float
    iterations: int
    converged: bool


def newton(
    function: ScalarFunction,
    initial: float,
    *,
    derivative_function: ScalarFunction | None = None,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> RootResult:
    """Executa Newton-Raphson sem esconder falhas de convergência."""
    current = _finite(initial, "estimativa inicial")
    tolerance = _finite(tolerance, "tolerância")
    if tolerance <= 0 or not 1 <= max_iterations <= 1_000_000:
        raise ValueError("limites inválidos")
    for iteration in range(max_iterations + 1):
        value = _finite(function(current), "resíduo")
        if abs(value) <= tolerance:
            return RootResult(current, value, iteration, True)
        if iteration == max_iterations:
            break
        slope = (
            _finite(derivative_function(current), "derivada")
            if derivative_function is not None
            else derivative(function, current, max(1e-7, abs(current) * 1e-7))
        )
        if slope == 0:
            return RootResult(current, value, iteration, False)
        candidate = current - value / slope
        if not math.isfinite(candidate):
            return RootResult(current, value, iteration, False)
        current = candidate
    residual = _finite(function(current), "resíduo")
    return RootResult(current, residual, max_iterations, False)


__all__ = ["RootResult", "derivative", "newton", "second_derivative", "simpson"]
