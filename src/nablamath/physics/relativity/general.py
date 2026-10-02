"""Explicit Schwarzschild reference geometry and weak-field observables.

This module implements one exact vacuum metric and selected invariants/observables.
It is not a generic Einstein-equation solver.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi, sin, sqrt

from .special import C_M_S

G_M3_KG_S2 = 6.67430e-11


@dataclass(frozen=True)
class SchwarzschildMetric:
    mass_kg: float

    def __post_init__(self) -> None:
        if not isfinite(self.mass_kg) or self.mass_kg <= 0:
            raise ValueError("Massa central deve ser positiva e finita")

    @property
    def schwarzschild_radius_m(self) -> float:
        return 2.0 * G_M3_KG_S2 * self.mass_kg / (C_M_S ** 2)

    def _outside(self, radius_m: float) -> float:
        if not isfinite(radius_m) or radius_m <= self.schwarzschild_radius_m:
            raise ValueError("Esta carta estática exige r > raio de Schwarzschild")
        return 1.0 - self.schwarzschild_radius_m / radius_m

    def diagonal(self, radius_m: float, theta_rad: float) -> tuple[float, float, float, float]:
        factor = self._outside(radius_m)
        if not isfinite(theta_rad):
            raise ValueError("theta deve ser finito")
        return (
            -factor * C_M_S ** 2,
            1.0 / factor,
            radius_m ** 2,
            radius_m ** 2 * sin(theta_rad) ** 2,
        )

    def static_clock_rate(self, radius_m: float) -> float:
        return sqrt(self._outside(radius_m))

    def kretschmann_m4_inverse(self, radius_m: float) -> float:
        self._outside(radius_m)
        return 48.0 * (G_M3_KG_S2 ** 2) * (self.mass_kg ** 2) / (C_M_S ** 4 * radius_m ** 6)

    def circular_orbit_angular_velocity_rad_s(self, radius_m: float) -> float:
        self._outside(radius_m)
        return sqrt(G_M3_KG_S2 * self.mass_kg / radius_m ** 3)

    def weak_field_periapsis_advance_rad_per_orbit(self, semi_major_axis_m: float, eccentricity: float) -> float:
        if not isfinite(semi_major_axis_m) or semi_major_axis_m <= 0:
            raise ValueError("Semieixo maior deve ser positivo e finito")
        if not isfinite(eccentricity) or not 0 <= eccentricity < 1:
            raise ValueError("Excentricidade deve satisfazer 0 <= e < 1")
        denominator = semi_major_axis_m * (1.0 - eccentricity ** 2) * C_M_S ** 2
        return 6.0 * pi * G_M3_KG_S2 * self.mass_kg / denominator


def minkowski_christoffel_cartesian() -> tuple[tuple[tuple[float, ...], ...], ...]:
    return tuple(tuple(tuple(0.0 for _ in range(4)) for _ in range(4)) for _ in range(4))


__all__ = ["G_M3_KG_S2", "SchwarzschildMetric", "minkowski_christoffel_cartesian"]
