"""Reproducible Brownian paths and Euler–Maruyama Itô SDE integration."""

from __future__ import annotations
from dataclasses import dataclass
import math
import random
from typing import Callable


@dataclass(frozen=True)
class StochasticPath:
    times: tuple[float, ...]
    values: tuple[float, ...]
    brownian: tuple[float, ...]
    seed: int


def euler_maruyama(initial: float, duration: float, steps: int,
                    drift: Callable[[float, float], float],
                    diffusion: Callable[[float, float], float], *, seed: int = 0) -> StochasticPath:
    if not math.isfinite(initial) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Estado e duração inválidos")
    if type(steps) is not int or not 1 <= steps <= 10_000_000:
        raise ValueError("steps fora do orçamento")
    generator, delta = random.Random(seed), duration / steps
    times, values, brownian = [0.0], [initial], [0.0]
    for index in range(steps):
        increment = math.sqrt(delta) * generator.gauss(0.0, 1.0)
        time, value = times[-1], values[-1]
        next_value = value + float(drift(time, value)) * delta + float(diffusion(time, value)) * increment
        if not math.isfinite(next_value):
            raise ArithmeticError(f"SDE produziu estado não finito no passo {index + 1}")
        times.append((index + 1) * delta)
        values.append(next_value)
        brownian.append(brownian[-1] + increment)
    return StochasticPath(tuple(times), tuple(values), tuple(brownian), seed)


def brownian_motion(duration: float, steps: int, *, seed: int = 0) -> StochasticPath:
    return euler_maruyama(0.0, duration, steps, lambda _t, _x: 0.0,
                          lambda _t, _x: 1.0, seed=seed)


__all__ = ["StochasticPath", "brownian_motion", "euler_maruyama"]
