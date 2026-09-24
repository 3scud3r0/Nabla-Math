"""Propagação radial de dois corpos com momento angular conservado."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

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
    """Integra (r, dr/dt) via RK4; v_t = h/r; sem orientação ou perturbações."""
    if not isfinite(mu_m3_s2) or mu_m3_s2 <= 0:
        raise ValueError("mu deve ser positivo e finito")
    if not isfinite(duration_s) or duration_s <= 0:
        raise ValueError("Duração deve ser positiva e finita")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1_000_000:
        raise ValueError("steps deve ser inteiro entre 1 e 1000000")
    h = initial.radius_m * initial.tangential_velocity_m_s
    dt = duration_s / steps
    r, vr = initial.radius_m, initial.radial_velocity_m_s

    def derivative(radius: float, radial_velocity: float) -> tuple[float, float]:
        if not isfinite(radius) or radius <= 0 or not isfinite(radial_velocity):
            raise ValueError("A integração saiu do domínio orbital")
        return radial_velocity, h**2 / radius**3 - mu_m3_s2 / radius**2

    for _ in range(steps):
        k1r, k1v = derivative(r, vr)
        k2r, k2v = derivative(r + dt*k1r/2, vr + dt*k1v/2)
        k3r, k3v = derivative(r + dt*k2r/2, vr + dt*k2v/2)
        k4r, k4v = derivative(r + dt*k3r, vr + dt*k3v)
        r += dt*(k1r + 2*k2r + 2*k3r + k4r)/6
        vr += dt*(k1v + 2*k2v + 2*k3v + k4v)/6
        derivative(r, vr)

    final = OrbitalState(r, vr, h/r, initial.epoch_s + duration_s, initial.frame)
    e0 = 0.5 * (initial.radial_velocity_m_s**2 + initial.tangential_velocity_m_s**2) - mu_m3_s2 / initial.radius_m
    e1 = 0.5 * (final.radial_velocity_m_s**2 + final.tangential_velocity_m_s**2) - mu_m3_s2 / final.radius_m
    return Propagation(final, duration_s, steps, e0, e1, abs(e1-e0),
                       ("point_mass", "two_body", "radial_reduced_model", "no_perturbations"))


__all__ = ["Propagation", "acceleration", "propagate_radial"]
