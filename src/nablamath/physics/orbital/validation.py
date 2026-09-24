"""Validações de consistência dos modelos orbitais, sem fonte observacional implícita."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from ...orbits import Orbit
from .dynamics import Propagation


@dataclass(frozen=True)
class Validation:
    passed: bool
    checks: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_orbit(orbit: Orbit) -> Validation:
    values = orbit.summary()
    checks = ("positive_period", "nonnegative_eccentricity", "vis_viva_defined")
    passed = values["period_s"] > 0 and values["eccentricity"] >= 0 and isclose(
        orbit.speed_m_s(orbit.pericenter_m) ** 2,
        orbit.mu_m3_s2 * (2 / orbit.pericenter_m - 1 / orbit.semimajor_axis_m),
        rel_tol=1e-12,
    )
    return Validation(passed, checks, () if passed else ("analytic check failed",))


def validate_propagation(result: Propagation, tolerance_j_kg: float = 1e-2) -> Validation:
    if tolerance_j_kg < 0:
        raise ValueError("Tolerância não pode ser negativa")
    passed = result.energy_error_j_kg <= tolerance_j_kg
    return Validation(passed, ("energy_error_within_tolerance",),
                      () if passed else ("refine time step or use a vector solver",))


__all__ = ["Validation", "validate_orbit", "validate_propagation"]
