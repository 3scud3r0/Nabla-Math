"""Differentiable periodic 1D viscous Burgers reference solver.

This is a finite-difference PDE solver used to exercise differentiable fluid
discretization. It is not a compressible/incompressible Navier-Stokes CFD code.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence, TypeAlias

from ...autodiff import Var

Scalar: TypeAlias = float | Var


def _value(x: Scalar) -> float:
    return x.value if isinstance(x, Var) else float(x)


@dataclass(frozen=True)
class BurgersResult:
    values: tuple[Scalar, ...]
    dx: float
    dt: float
    steps: int
    viscosity_m2_s: Scalar
    assumptions: tuple[str, ...] = (
        "one_dimensional", "periodic_boundary", "uniform_grid",
        "explicit_central_convection", "explicit_central_diffusion",
    )

    @property
    def mean(self) -> Scalar:
        total: Scalar = 0.0
        for value in self.values:
            total = total + value
        return total / len(self.values)

    def energy(self) -> Scalar:
        total: Scalar = 0.0
        for value in self.values:
            total = total + value * value
        return total * self.dx / 2


def solve_burgers_periodic(initial: Sequence[Scalar], length_m: float, duration_s: float,
                           viscosity_m2_s: Scalar, steps: int) -> BurgersResult:
    values = tuple(initial)
    n = len(values)
    if n < 3:
        raise ValueError("Burgers 1D requer ao menos três células")
    if not math.isfinite(length_m) or not math.isfinite(duration_s) or length_m <= 0 or duration_s <= 0:
        raise ValueError("Comprimento e duração devem ser positivos e finitos")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1_000_000:
        raise ValueError("steps deve ser inteiro entre 1 e 1000000")
    viscosity_value = _value(viscosity_m2_s)
    if not math.isfinite(viscosity_value) or viscosity_value < 0:
        raise ValueError("Viscosidade deve ser finita e não negativa")
    if any(not math.isfinite(_value(value)) for value in values):
        raise ValueError("Estado inicial contém valor não finito")
    dx = length_m / n
    dt = duration_s / steps
    max_speed = max(abs(_value(value)) for value in values)
    convective_limit = math.inf if max_speed == 0 else 0.5 * dx / max_speed
    diffusive_limit = math.inf if viscosity_value == 0 else 0.45 * dx * dx / viscosity_value
    if dt > min(convective_limit, diffusive_limit):
        raise ValueError("Passo temporal viola o limite explícito de estabilidade do solver")
    coefficient_convection = dt / (2 * dx)
    coefficient_diffusion = viscosity_m2_s * dt / (dx * dx)
    current = values
    for _ in range(steps):
        next_values: list[Scalar] = []
        for i, center in enumerate(current):
            left = current[(i - 1) % n]
            right = current[(i + 1) % n]
            convection = center * coefficient_convection * (right - left)
            diffusion = coefficient_diffusion * (right - 2 * center + left)
            next_values.append(center - convection + diffusion)
        current = tuple(next_values)
    return BurgersResult(current, dx, dt, steps, viscosity_m2_s)


__all__ = ["Scalar", "BurgersResult", "solve_burgers_periodic"]