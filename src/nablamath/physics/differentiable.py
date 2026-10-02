"""Differentiable reduced-order physics built on NablaMath reverse autodiff.

These models are explicit reference surrogates, not CFD/FEA/MHD solvers. Their
purpose is to make end-to-end sensitivities testable today while retaining clear
assumptions and a path toward higher-fidelity differentiable backends.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Sequence, TypeAlias

from ..autodiff import Var, exp

Scalar: TypeAlias = float | Var
State: TypeAlias = tuple[Scalar, ...]
RHS: TypeAlias = Callable[[float, State], State]


def rk4_integrate(rhs: RHS, initial: Sequence[Scalar], t0: float, t1: float, steps: int) -> State:
    """Fixed-step RK4 that preserves reverse-mode dependencies in state values."""
    if not isfinite(t0) or not isfinite(t1) or t1 <= t0:
        raise ValueError("Intervalo temporal deve ser finito e crescente")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1_000_000:
        raise ValueError("steps deve ser inteiro entre 1 e 1000000")
    state = tuple(initial)
    if not state:
        raise ValueError("Estado não pode ser vazio")
    dt = (t1 - t0) / steps

    def check(value: State) -> State:
        if len(value) != len(state):
            raise ValueError("RHS alterou a dimensão do estado")
        return tuple(value)

    def shifted(base: State, tangent: State, scale: float) -> State:
        return tuple(x + scale * dx for x, dx in zip(base, tangent))

    time = t0
    for _ in range(steps):
        k1 = check(rhs(time, state))
        k2 = check(rhs(time + dt / 2, shifted(state, k1, dt / 2)))
        k3 = check(rhs(time + dt / 2, shifted(state, k2, dt / 2)))
        k4 = check(rhs(time + dt, shifted(state, k3, dt)))
        state = tuple(
            x + dt * (a + 2 * b + 2 * c + d) / 6
            for x, a, b, c, d in zip(state, k1, k2, k3, k4)
        )
        time += dt
    return state


def propagate_radial_differentiable(mu_m3_s2: Scalar, radius_m: Scalar, radial_velocity_m_s: Scalar,
                                    tangential_velocity_m_s: Scalar, duration_s: float,
                                    steps: int = 1000) -> tuple[Scalar, Scalar, Scalar]:
    """Two-body radial reduction equivalent to the existing RK4 model, but differentiable."""
    if not isfinite(duration_s) or duration_s <= 0:
        raise ValueError("Duração deve ser positiva e finita")
    h = radius_m * tangential_velocity_m_s

    def rhs(_: float, state: State) -> State:
        radius, radial_velocity = state
        radial_acceleration = h * h / (radius ** 3) - mu_m3_s2 / (radius ** 2)
        return radial_velocity, radial_acceleration

    final_radius, final_radial = rk4_integrate(rhs, (radius_m, radial_velocity_m_s), 0.0, duration_s, steps)
    final_tangential = h / final_radius
    return final_radius, final_radial, final_tangential


@dataclass(frozen=True)
class OrbitalSensitivity:
    final_radius_m: float
    final_radial_velocity_m_s: float
    final_tangential_velocity_m_s: float
    d_final_radius_d_mu: float
    d_final_radius_d_radius0: float
    d_final_radius_d_radial_velocity0: float
    d_final_radius_d_tangential_velocity0: float


def orbital_terminal_sensitivity(mu_m3_s2: float, radius_m: float, radial_velocity_m_s: float,
                                 tangential_velocity_m_s: float, duration_s: float,
                                 steps: int = 1000) -> OrbitalSensitivity:
    mu = Var(mu_m3_s2)
    radius = Var(radius_m)
    radial = Var(radial_velocity_m_s)
    tangential = Var(tangential_velocity_m_s)
    final_radius, final_radial, final_tangential = propagate_radial_differentiable(
        mu, radius, radial, tangential, duration_s, steps
    )
    assert isinstance(final_radius, Var) and isinstance(final_radial, Var) and isinstance(final_tangential, Var)
    final_radius.backward()
    return OrbitalSensitivity(
        final_radius.value, final_radial.value, final_tangential.value,
        mu.grad, radius.grad, radial.grad, tangential.grad,
    )


@dataclass(frozen=True)
class ReentryResult:
    altitude_m: Scalar
    downward_speed_m_s: Scalar
    heat_load_proxy: Scalar
    assumptions: tuple[str, ...] = (
        "one_dimensional_vertical", "exponential_atmosphere", "constant_gravity",
        "constant_ballistic_coefficient", "continuum_drag_surrogate",
    )


def vertical_reentry_differentiable(altitude_m: Scalar, downward_speed_m_s: Scalar,
                                    ballistic_coefficient_kg_m2: Scalar, duration_s: float,
                                    steps: int = 500, *, sea_level_density_kg_m3: float = 1.225,
                                    scale_height_m: float = 8500.0, gravity_m_s2: float = 9.80665,
                                    heat_coefficient: float = 1.0) -> ReentryResult:
    """Differentiable vertical-entry surrogate with drag and integrated heating proxy.

    The heating proxy is heat_coefficient * sqrt(rho) * v^3 and is intentionally
    dimensionless unless the caller supplies a calibrated dimensional coefficient.
    """
    for value in (duration_s, sea_level_density_kg_m3, scale_height_m, gravity_m_s2, heat_coefficient):
        if not isfinite(value):
            raise ValueError("Parâmetros escalares precisam ser finitos")
    if duration_s <= 0 or sea_level_density_kg_m3 <= 0 or scale_height_m <= 0 or heat_coefficient < 0:
        raise ValueError("Parâmetros físicos fora do domínio")

    def rhs(_: float, state: State) -> State:
        altitude, speed, _heat = state
        density = sea_level_density_kg_m3 * exp(-altitude / scale_height_m)
        drag_acceleration = 0.5 * density * speed * speed / ballistic_coefficient_kg_m2
        sqrt_density = exp(0.5 * (density.log() if isinstance(density, Var) else __import__("math").log(density)))
        heating = heat_coefficient * sqrt_density * speed * speed * speed
        return -speed, gravity_m_s2 - drag_acceleration, heating

    altitude, speed, heat = rk4_integrate(rhs, (altitude_m, downward_speed_m_s, 0.0), 0.0, duration_s, steps)
    return ReentryResult(altitude, speed, heat)


__all__ = [
    "Scalar", "State", "rk4_integrate", "propagate_radial_differentiable",
    "OrbitalSensitivity", "orbital_terminal_sensitivity", "ReentryResult",
    "vertical_reentry_differentiable",
]