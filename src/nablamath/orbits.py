"""Órbitas keplerianas ideais de dois corpos; SI, sem perturbações nem controle."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite, pi, sqrt

EARTH_MU_M3_S2 = 3.986004418e14
EARTH_EQUATORIAL_RADIUS_M = 6_378_137.0


def _positive(value: float, name: str) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} deve ser finito e positivo")


@dataclass(frozen=True)
class Orbit:
    """Elementos escalares de uma órbita elíptica (sem inclinação/orientação)."""

    mu_m3_s2: float
    pericenter_m: float
    apocenter_m: float

    def __post_init__(self) -> None:
        for name in ("mu_m3_s2", "pericenter_m", "apocenter_m"):
            _positive(getattr(self, name), name)
        if self.apocenter_m < self.pericenter_m:
            raise ValueError("Apocentro deve ser maior ou igual ao pericentro")

    @property
    def semimajor_axis_m(self) -> float:
        return (self.pericenter_m + self.apocenter_m) / 2

    def speed_m_s(self, radius_m: float) -> float:
        _positive(radius_m, "radius_m")
        if not self.pericenter_m <= radius_m <= self.apocenter_m:
            raise ValueError("Raio fora da órbita descrita")
        return sqrt(self.mu_m3_s2 * (2 / radius_m - 1 / self.semimajor_axis_m))

    def summary(self) -> dict:
        a = self.semimajor_axis_m
        vp = self.speed_m_s(self.pericenter_m)
        va = self.speed_m_s(self.apocenter_m)
        return {**asdict(self), "semimajor_axis_m": a,
                "eccentricity": (self.apocenter_m - self.pericenter_m) / (2 * a),
                "period_s": 2 * pi * sqrt(a**3 / self.mu_m3_s2),
                "pericenter_speed_m_s": vp, "apocenter_speed_m_s": va,
                "specific_energy_j_kg": -self.mu_m3_s2 / (2 * a),
                "specific_angular_momentum_m2_s": self.pericenter_m * vp,
                "assumptions": ["two_body", "point_mass", "no_atmosphere", "no_perturbations"],
                "verification": "analytic_vis_viva; numerical_floating_point", "formal_proof": None}


def earth_circular_orbit(altitude_m: float) -> Orbit:
    if not isfinite(altitude_m) or altitude_m < 0:
        raise ValueError("Altitude deve ser finita e não negativa")
    radius = EARTH_EQUATORIAL_RADIUS_M + altitude_m
    return Orbit(EARTH_MU_M3_S2, radius, radius)
