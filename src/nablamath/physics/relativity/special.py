"""Reference special-relativity primitives in SI units."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

C_M_S = 299_792_458.0


def _speed(vx: float, vy: float = 0.0, vz: float = 0.0) -> float:
    if not all(isfinite(v) for v in (vx, vy, vz)):
        raise ValueError("Velocidade deve ser finita")
    return sqrt(vx * vx + vy * vy + vz * vz)


def lorentz_gamma(v_m_s: float) -> float:
    speed = abs(float(v_m_s))
    if not isfinite(speed) or speed >= C_M_S:
        raise ValueError("Transformação de Lorentz exige |v| < c")
    beta = speed / C_M_S
    return 1.0 / sqrt(1.0 - beta * beta)


@dataclass(frozen=True)
class FourPosition:
    t_s: float
    x_m: float
    y_m: float = 0.0
    z_m: float = 0.0

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.t_s, self.x_m, self.y_m, self.z_m)):
            raise ValueError("Quatro-posição deve ser finita")


def minkowski_interval_squared(event: FourPosition) -> float:
    return (C_M_S * event.t_s) ** 2 - event.x_m ** 2 - event.y_m ** 2 - event.z_m ** 2


def lorentz_boost_x(event: FourPosition, velocity_m_s: float) -> FourPosition:
    gamma = lorentz_gamma(velocity_m_s)
    v = float(velocity_m_s)
    t = gamma * (event.t_s - v * event.x_m / (C_M_S * C_M_S))
    x = gamma * (event.x_m - v * event.t_s)
    return FourPosition(t, x, event.y_m, event.z_m)


def compose_collinear_velocities(u_m_s: float, v_m_s: float) -> float:
    if abs(u_m_s) >= C_M_S or abs(v_m_s) >= C_M_S:
        raise ValueError("Velocidades de entrada devem ser subluminais")
    result = (u_m_s + v_m_s) / (1.0 + u_m_s * v_m_s / (C_M_S * C_M_S))
    if abs(result) >= C_M_S * (1 + 1e-14):
        raise ArithmeticError("Composição produziu velocidade superluminal")
    return result


@dataclass(frozen=True)
class FourMomentum:
    energy_j: float
    px_kg_m_s: float
    py_kg_m_s: float
    pz_kg_m_s: float
    rest_mass_kg: float

    @property
    def momentum_squared(self) -> float:
        return self.px_kg_m_s ** 2 + self.py_kg_m_s ** 2 + self.pz_kg_m_s ** 2

    @property
    def invariant_j2(self) -> float:
        return self.energy_j ** 2 - self.momentum_squared * C_M_S ** 2


def four_momentum(rest_mass_kg: float, vx_m_s: float, vy_m_s: float = 0.0, vz_m_s: float = 0.0) -> FourMomentum:
    if not isfinite(rest_mass_kg) or rest_mass_kg < 0:
        raise ValueError("Massa de repouso deve ser finita e não negativa")
    speed = _speed(vx_m_s, vy_m_s, vz_m_s)
    gamma = lorentz_gamma(speed)
    energy = gamma * rest_mass_kg * C_M_S ** 2
    factor = gamma * rest_mass_kg
    return FourMomentum(energy, factor * vx_m_s, factor * vy_m_s, factor * vz_m_s, rest_mass_kg)


def mass_shell_relative_error(momentum: FourMomentum) -> float:
    expected = (momentum.rest_mass_kg * C_M_S ** 2) ** 2
    scale = max(abs(expected), abs(momentum.invariant_j2), 1.0)
    return abs(momentum.invariant_j2 - expected) / scale


__all__ = [
    "C_M_S", "FourPosition", "FourMomentum", "lorentz_gamma", "minkowski_interval_squared",
    "lorentz_boost_x", "compose_collinear_velocities", "four_momentum", "mass_shell_relative_error",
]
