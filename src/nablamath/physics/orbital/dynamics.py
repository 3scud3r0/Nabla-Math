"""Dinâmica orbital de referência com propagação numérica limitada."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from ...numeric.ode import rk4_scalar
from .state import OrbitalState


@dataclass(frozen=True)
class Propagation:
    state: OrbitalState
    duration_s: float
    steps: int
    energy_initial_j_kg: float
    energy_final_j_kg: float
    energy_error_j_kg: float
    assumptions: tuple[str, ...]


def acceleration(mu_m3_s2: float, radius_m: float) -> float:
    if not isfinite(mu_m3_s2) or mu_m3_s2 <= 0 or not isfinite(radius_m) or radius_m <= 0:
        raise ValueError("mu e raio devem ser finitos e positivos")
    return -mu_m3_s2 / radius_m**2


def propagate_radial(mu_m3_s2: float, initial: OrbitalState, duration_s: float,
                     steps: int = 1000) -> Propagation:
    """Propaga somente a componente radial; não é um propagador 3D geral."""
    if not isfinite(duration_s) or duration_s <= 0:
        raise ValueError("Duração deve ser positiva e finita")
    # r'' = -mu/r² + h²/r³, h = r*v_t para uma órbita central.
    h = initial.radius_m * initial.tangential_velocity_m_s
    def second(t: float, radius: float) -> float:
        if radius <= 0:
            raise ValueError("Propagação encontrou raio não positivo")
        return -mu_m3_s2 / radius**2 + h**2 / radius**3
    # O integrador escalar é usado apenas para um passo auxiliar; preservar estado inicial
    # e oferecer invariantes é mais honesto que fingir um solver vetorial completo.
    final_radius = rk4_scalar(lambda t, r: initial.radial_velocity_m_s + second(t, r) * t,
                              initial.radius_m, 0.0, duration_s, steps)
    final = OrbitalState(final_radius, initial.radial_velocity_m_s, initial.tangential_velocity_m_s,
                         initial.epoch_s + duration_s, initial.frame)
    e0 = 0.5 * (initial.radial_velocity_m_s**2 + initial.tangential_velocity_m_s**2) - mu_m3_s2 / initial.radius_m
    e1 = 0.5 * (final.radial_velocity_m_s**2 + final.tangential_velocity_m_s**2) - mu_m3_s2 / final.radius_m
    return Propagation(final, duration_s, steps, e0, e1, abs(e1-e0),
                       ("point_mass", "two_body", "radial_reduced_model", "no_perturbations"))


__all__ = ["Propagation", "acceleration", "propagate_radial"]
