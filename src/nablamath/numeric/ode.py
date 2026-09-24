"""RK4 fixo para estudos controlados, com incerteza estimada por refinamento."""

from math import isfinite
from typing import Callable


def rk4_scalar(f: Callable[[float, float], float], y0: float, t0: float,
               t1: float, steps: int) -> float:
    if type(steps) is not int or steps < 1 or steps > 10_000_000:
        raise ValueError("Número de passos fora do intervalo")
    if not all(isfinite(v) for v in (y0, t0, t1)) or t1 <= t0:
        raise ValueError("Tempo e condição inicial devem ser finitos e ordenados")
    h = (t1-t0)/steps
    t, y = t0, y0
    for _ in range(steps):
        k1 = f(t, y)
        k2 = f(t+h/2, y+h*k1/2)
        k3 = f(t+h/2, y+h*k2/2)
        k4 = f(t+h, y+h*k3)
        if not all(isfinite(k) for k in (k1, k2, k3, k4)):
            raise ValueError("Derivada não finita durante a integração")
        y += h*(k1 + 2*k2 + 2*k3 + k4)/6
        t += h
        if not isfinite(y):
            raise ValueError("Solução deixou de ser finita")
    return y


def refine_error(f: Callable[[float, float], float], y0: float,
                 t0: float, t1: float, steps: int) -> tuple[float, float]:
    """Diferença h/2 e h; indicador de convergência, não limite rigoroso."""
    coarse = rk4_scalar(f, y0, t0, t1, steps)
    fine = rk4_scalar(f, y0, t0, t1, 2*steps)
    return fine, abs(fine-coarse)
