"""Differentiable 2D periodic incompressible Navier-Stokes reference solver.

The implementation uses a first-order explicit predictor plus a pressure-projection
step on a uniform periodic grid.  The pressure Poisson equation is approximated by
a fixed number of Jacobi iterations so the arithmetic path remains differentiable
with NablaMath's scalar reverse-mode `Var`.

This module is a verification/reference discretization.  It is not a production
CFD solver: it has no turbulence model, shocks, immersed boundaries, adaptive
meshes, high-order reconstruction, MPI decomposition or validated engineering
error model.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence, TypeAlias

from ...autodiff import Var

Scalar: TypeAlias = float | Var
Field2D: TypeAlias = tuple[tuple[Scalar, ...], ...]


def _value(x: Scalar) -> float:
    return x.value if isinstance(x, Var) else float(x)


def _validate_field(field: Sequence[Sequence[Scalar]], name: str) -> tuple[tuple[Scalar, ...], ...]:
    rows = tuple(tuple(row) for row in field)
    if len(rows) < 3 or len(rows[0]) < 3:
        raise ValueError(f"{name} requer grade ao menos 3x3")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError(f"{name} precisa ser retangular")
    if any(not math.isfinite(_value(item)) for row in rows for item in row):
        raise ValueError(f"{name} contém valor não finito")
    return rows


def _zeros(ny: int, nx: int) -> list[list[Scalar]]:
    return [[0.0 for _ in range(nx)] for _ in range(ny)]


def _mean(field: Sequence[Sequence[Scalar]]) -> Scalar:
    total: Scalar = 0.0
    count = 0
    for row in field:
        for item in row:
            total = total + item
            count += 1
    return total / count


def _pressure_poisson_periodic(
    rhs: Sequence[Sequence[Scalar]],
    dx: float,
    dy: float,
    iterations: int,
) -> Field2D:
    ny, nx = len(rhs), len(rhs[0])
    pressure: list[list[Scalar]] = _zeros(ny, nx)
    dx2, dy2 = dx * dx, dy * dy
    denominator = 2.0 * (dx2 + dy2)

    for _ in range(iterations):
        nxt = _zeros(ny, nx)
        for j in range(ny):
            jm, jp = (j - 1) % ny, (j + 1) % ny
            for i in range(nx):
                im, ip = (i - 1) % nx, (i + 1) % nx
                nxt[j][i] = (
                    (pressure[j][ip] + pressure[j][im]) * dy2
                    + (pressure[jp][i] + pressure[jm][i]) * dx2
                    - rhs[j][i] * dx2 * dy2
                ) / denominator
        # The periodic Poisson operator has a constant null-space.  Removing the
        # mean picks a deterministic gauge without changing pressure gradients.
        mean_pressure = _mean(nxt)
        pressure = [[item - mean_pressure for item in row] for row in nxt]
    return tuple(tuple(row) for row in pressure)


@dataclass(frozen=True)
class IncompressibleFlowResult:
    u_m_s: Field2D
    v_m_s: Field2D
    pressure_pa: Field2D
    dx_m: float
    dy_m: float
    dt_s: float
    steps: int
    density_kg_m3: float
    kinematic_viscosity_m2_s: Scalar
    pressure_iterations: int
    assumptions: tuple[str, ...] = (
        "two_dimensional",
        "incompressible",
        "newtonian",
        "constant_density",
        "periodic_boundaries",
        "uniform_cartesian_grid",
        "explicit_central_advection_diffusion",
        "pressure_projection",
        "fixed_jacobi_pressure_iterations",
    )

    def kinetic_energy(self) -> Scalar:
        total: Scalar = 0.0
        for row_u, row_v in zip(self.u_m_s, self.v_m_s):
            for u, v in zip(row_u, row_v):
                total = total + u * u + v * v
        return 0.5 * self.density_kg_m3 * total * self.dx_m * self.dy_m

    def divergence_l2(self) -> float:
        ny, nx = len(self.u_m_s), len(self.u_m_s[0])
        total = 0.0
        for j in range(ny):
            jm, jp = (j - 1) % ny, (j + 1) % ny
            for i in range(nx):
                im, ip = (i - 1) % nx, (i + 1) % nx
                du_dx = (_value(self.u_m_s[j][ip]) - _value(self.u_m_s[j][im])) / (2 * self.dx_m)
                dv_dy = (_value(self.v_m_s[jp][i]) - _value(self.v_m_s[jm][i])) / (2 * self.dy_m)
                divergence = du_dx + dv_dy
                total += divergence * divergence
        return math.sqrt(total / (nx * ny))


def solve_incompressible_periodic(
    u0_m_s: Sequence[Sequence[Scalar]],
    v0_m_s: Sequence[Sequence[Scalar]],
    width_m: float,
    height_m: float,
    duration_s: float,
    kinematic_viscosity_m2_s: Scalar,
    *,
    density_kg_m3: float = 1.0,
    steps: int = 10,
    pressure_iterations: int = 40,
) -> IncompressibleFlowResult:
    """Advance a periodic incompressible velocity field with a projection method."""
    u = _validate_field(u0_m_s, "u")
    v = _validate_field(v0_m_s, "v")
    if (len(u), len(u[0])) != (len(v), len(v[0])):
        raise ValueError("u e v precisam ter o mesmo shape")
    for value, name in ((width_m, "width_m"), (height_m, "height_m"),
                        (duration_s, "duration_s"), (density_kg_m3, "density_kg_m3")):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} deve ser positivo e finito")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1_000_000:
        raise ValueError("steps deve ser inteiro entre 1 e 1000000")
    if (isinstance(pressure_iterations, bool) or not isinstance(pressure_iterations, int)
            or not 1 <= pressure_iterations <= 100_000):
        raise ValueError("pressure_iterations deve ser inteiro entre 1 e 100000")

    viscosity = _value(kinematic_viscosity_m2_s)
    if not math.isfinite(viscosity) or viscosity < 0:
        raise ValueError("viscosidade cinemática deve ser finita e não negativa")

    ny, nx = len(u), len(u[0])
    dx, dy = width_m / nx, height_m / ny
    dt = duration_s / steps
    max_speed = max(math.hypot(_value(uu), _value(vv))
                    for row_u, row_v in zip(u, v) for uu, vv in zip(row_u, row_v))
    convective_limit = math.inf if max_speed == 0 else 0.35 * min(dx, dy) / max_speed
    diffusive_limit = math.inf if viscosity == 0 else 0.20 / (
        viscosity * (1.0 / (dx * dx) + 1.0 / (dy * dy))
    )
    if dt > min(convective_limit, diffusive_limit):
        raise ValueError("Passo temporal viola o limite conservador de estabilidade CFD")

    pressure: Field2D = tuple(tuple(0.0 for _ in range(nx)) for _ in range(ny))
    for _ in range(steps):
        u_star = _zeros(ny, nx)
        v_star = _zeros(ny, nx)
        for j in range(ny):
            jm, jp = (j - 1) % ny, (j + 1) % ny
            for i in range(nx):
                im, ip = (i - 1) % nx, (i + 1) % nx
                uc, vc = u[j][i], v[j][i]
                du_dx = (u[j][ip] - u[j][im]) / (2 * dx)
                du_dy = (u[jp][i] - u[jm][i]) / (2 * dy)
                dv_dx = (v[j][ip] - v[j][im]) / (2 * dx)
                dv_dy = (v[jp][i] - v[jm][i]) / (2 * dy)
                lap_u = ((u[j][ip] - 2 * uc + u[j][im]) / (dx * dx)
                         + (u[jp][i] - 2 * uc + u[jm][i]) / (dy * dy))
                lap_v = ((v[j][ip] - 2 * vc + v[j][im]) / (dx * dx)
                         + (v[jp][i] - 2 * vc + v[jm][i]) / (dy * dy))
                u_star[j][i] = uc + dt * (-uc * du_dx - vc * du_dy
                                          + kinematic_viscosity_m2_s * lap_u)
                v_star[j][i] = vc + dt * (-uc * dv_dx - vc * dv_dy
                                          + kinematic_viscosity_m2_s * lap_v)

        rhs = _zeros(ny, nx)
        for j in range(ny):
            jm, jp = (j - 1) % ny, (j + 1) % ny
            for i in range(nx):
                im, ip = (i - 1) % nx, (i + 1) % nx
                divergence = ((u_star[j][ip] - u_star[j][im]) / (2 * dx)
                              + (v_star[jp][i] - v_star[jm][i]) / (2 * dy))
                rhs[j][i] = density_kg_m3 * divergence / dt

        pressure = _pressure_poisson_periodic(rhs, dx, dy, pressure_iterations)
        next_u = _zeros(ny, nx)
        next_v = _zeros(ny, nx)
        for j in range(ny):
            jm, jp = (j - 1) % ny, (j + 1) % ny
            for i in range(nx):
                im, ip = (i - 1) % nx, (i + 1) % nx
                dp_dx = (pressure[j][ip] - pressure[j][im]) / (2 * dx)
                dp_dy = (pressure[jp][i] - pressure[jm][i]) / (2 * dy)
                next_u[j][i] = u_star[j][i] - dt * dp_dx / density_kg_m3
                next_v[j][i] = v_star[j][i] - dt * dp_dy / density_kg_m3
        u = tuple(tuple(row) for row in next_u)
        v = tuple(tuple(row) for row in next_v)

    return IncompressibleFlowResult(
        u, v, pressure, dx, dy, dt, steps, density_kg_m3,
        kinematic_viscosity_m2_s, pressure_iterations,
    )


__all__ = [
    "Scalar", "Field2D", "IncompressibleFlowResult", "solve_incompressible_periodic",
]
