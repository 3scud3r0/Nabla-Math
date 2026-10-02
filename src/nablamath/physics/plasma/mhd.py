"""Differentiable linear resistive-MHD Alfvén-wave reference solver.

The model is the 1D linearization of incompressible MHD around a uniform guide
field B0.  It evolves transverse velocity u and magnetic perturbation b on a
periodic grid:

    du/dt = (B0/(mu0*rho)) db/dx + nu d²u/dx²
    db/dt = B0 du/dx + eta d²b/dx²

where eta is magnetic diffusivity and nu is kinematic viscosity.

This is deliberately a reduced verification model, not a nonlinear multi-fluid,
Hall-MHD, relativistic-MHD or plasma-kinetics solver.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence, TypeAlias

from ...autodiff import Var

Scalar: TypeAlias = float | Var
MU0 = 4.0e-7 * math.pi


def _value(x: Scalar) -> float:
    return x.value if isinstance(x, Var) else float(x)


@dataclass(frozen=True)
class AlfvenResult:
    velocity_m_s: tuple[Scalar, ...]
    magnetic_perturbation_t: tuple[Scalar, ...]
    dx_m: float
    dt_s: float
    steps: int
    density_kg_m3: float
    guide_field_t: float
    magnetic_diffusivity_m2_s: Scalar
    kinematic_viscosity_m2_s: Scalar
    assumptions: tuple[str, ...] = (
        "linearized_mhd",
        "one_dimensional",
        "periodic_boundary",
        "uniform_guide_field",
        "constant_density",
        "incompressible_transverse_perturbations",
        "scalar_resistivity",
        "scalar_viscosity",
        "explicit_central_difference",
    )

    @property
    def alfven_speed_m_s(self) -> float:
        return abs(self.guide_field_t) / math.sqrt(MU0 * self.density_kg_m3)

    def energy_j_per_m2(self) -> Scalar:
        total: Scalar = 0.0
        for velocity, magnetic in zip(self.velocity_m_s, self.magnetic_perturbation_t):
            total = total + (
                0.5 * self.density_kg_m3 * velocity * velocity
                + magnetic * magnetic / (2.0 * MU0)
            )
        return total * self.dx_m


def solve_linear_resistive_alfven(
    velocity0_m_s: Sequence[Scalar],
    magnetic0_t: Sequence[Scalar],
    length_m: float,
    duration_s: float,
    density_kg_m3: float,
    guide_field_t: float,
    magnetic_diffusivity_m2_s: Scalar,
    kinematic_viscosity_m2_s: Scalar = 0.0,
    *,
    steps: int = 10,
) -> AlfvenResult:
    velocity = tuple(velocity0_m_s)
    magnetic = tuple(magnetic0_t)
    n = len(velocity)
    if n < 3 or len(magnetic) != n:
        raise ValueError("MHD 1D requer vetores de mesmo tamanho com ao menos três células")
    if any(not math.isfinite(_value(x)) for x in velocity + magnetic):
        raise ValueError("Estado MHD inicial contém valor não finito")
    for value, name in (
        (length_m, "length_m"),
        (duration_s, "duration_s"),
        (density_kg_m3, "density_kg_m3"),
    ):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} deve ser positivo e finito")
    if not math.isfinite(guide_field_t) or guide_field_t == 0:
        raise ValueError("guide_field_t deve ser finito e não nulo")
    eta = _value(magnetic_diffusivity_m2_s)
    nu = _value(kinematic_viscosity_m2_s)
    if not math.isfinite(eta) or eta < 0 or not math.isfinite(nu) or nu < 0:
        raise ValueError("Difusividades precisam ser finitas e não negativas")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1_000_000:
        raise ValueError("steps deve ser inteiro entre 1 e 1000000")

    dx = length_m / n
    dt = duration_s / steps
    alfven_speed = abs(guide_field_t) / math.sqrt(MU0 * density_kg_m3)
    wave_limit = 0.40 * dx / alfven_speed
    max_diffusivity = max(eta, nu)
    diffusion_limit = math.inf if max_diffusivity == 0 else 0.40 * dx * dx / max_diffusivity
    if dt > min(wave_limit, diffusion_limit):
        raise ValueError("Passo temporal viola estabilidade explícita do solver MHD")

    coupling_u = guide_field_t / (MU0 * density_kg_m3)
    for _ in range(steps):
        next_velocity: list[Scalar] = []
        next_magnetic: list[Scalar] = []
        for i in range(n):
            im, ip = (i - 1) % n, (i + 1) % n
            du_dx = (velocity[ip] - velocity[im]) / (2.0 * dx)
            db_dx = (magnetic[ip] - magnetic[im]) / (2.0 * dx)
            lap_u = (velocity[ip] - 2.0 * velocity[i] + velocity[im]) / (dx * dx)
            lap_b = (magnetic[ip] - 2.0 * magnetic[i] + magnetic[im]) / (dx * dx)
            next_velocity.append(
                velocity[i] + dt * (coupling_u * db_dx + kinematic_viscosity_m2_s * lap_u)
            )
            next_magnetic.append(
                magnetic[i] + dt * (guide_field_t * du_dx + magnetic_diffusivity_m2_s * lap_b)
            )
        velocity = tuple(next_velocity)
        magnetic = tuple(next_magnetic)

    return AlfvenResult(
        velocity,
        magnetic,
        dx,
        dt,
        steps,
        density_kg_m3,
        guide_field_t,
        magnetic_diffusivity_m2_s,
        kinematic_viscosity_m2_s,
    )


__all__ = ["Scalar", "MU0", "AlfvenResult", "solve_linear_resistive_alfven"]
