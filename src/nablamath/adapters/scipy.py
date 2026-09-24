"""Ponte opcional para ``scipy.integrate.solve_ivp`` com tolerâncias registradas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class ODESolution:
    t: tuple[float, ...]
    y: tuple[tuple[float, ...], ...]
    method: str
    rtol: float
    atol: float
    backend: str = "scipy.solve_ivp"


def solve_ivp(fun: Callable, interval: tuple[float, float], initial: Sequence[float], *,
              method: str = "RK45", rtol: float = 1e-8, atol: float = 1e-10) -> ODESolution:
    if not 0 < rtol < 1 or not 0 < atol < 1:
        raise ValueError("rtol e atol devem estar entre zero e um")
    try:
        from scipy.integrate import solve_ivp as _solve
    except ImportError as exc:
        raise RuntimeError("Instale o extra científico para usar SciPy") from exc
    result = _solve(fun, interval, initial, method=method, rtol=rtol, atol=atol)
    if not result.success:
        raise RuntimeError(result.message)
    return ODESolution(tuple(float(x) for x in result.t),
                       tuple(tuple(float(v) for v in row) for row in result.y),
                       method, rtol, atol)


__all__ = ["ODESolution", "solve_ivp"]
