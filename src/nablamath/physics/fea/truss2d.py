"""Differentiable planar 2D truss finite-element reference solver.

Each element is a two-node linear axial bar embedded in the XY plane.  Geometry
is fixed in the reference configuration while Young's modulus and area may be
NablaMath `Var` objects, so displacements, stresses and compliance remain
differentiable.

This is a small-strain linear truss solver, not 2D continuum elasticity, shells,
contact, geometric/material nonlinearity or 3D structural FEA.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence, TypeAlias

from ...autodiff import Var
from .bar import solve_linear_system

Scalar: TypeAlias = float | Var
Point2D: TypeAlias = tuple[float, float]


def _value(x: Scalar) -> float:
    return x.value if isinstance(x, Var) else float(x)


@dataclass(frozen=True)
class TrussElement:
    node_i: int
    node_j: int
    area_m2: Scalar
    young_pa: Scalar

    def __post_init__(self) -> None:
        if isinstance(self.node_i, bool) or isinstance(self.node_j, bool):
            raise ValueError("Índices de nós precisam ser inteiros")
        if not isinstance(self.node_i, int) or not isinstance(self.node_j, int):
            raise ValueError("Índices de nós precisam ser inteiros")
        if self.node_i == self.node_j:
            raise ValueError("Elemento de treliça precisa conectar dois nós distintos")
        if not math.isfinite(_value(self.area_m2)) or _value(self.area_m2) <= 0:
            raise ValueError("Área do elemento deve ser positiva e finita")
        if not math.isfinite(_value(self.young_pa)) or _value(self.young_pa) <= 0:
            raise ValueError("Módulo de Young deve ser positivo e finito")


@dataclass(frozen=True)
class PlanarTrussResult:
    displacements_m: tuple[tuple[Scalar, Scalar], ...]
    reactions_n: tuple[tuple[Scalar, Scalar], ...]
    element_strain: tuple[Scalar, ...]
    element_stress_pa: tuple[Scalar, ...]
    element_axial_force_n: tuple[Scalar, ...]
    compliance_j: Scalar
    assumptions: tuple[str, ...] = (
        "planar_truss",
        "linear_elastic",
        "small_strain",
        "pin_jointed_axial_elements",
        "fixed_reference_geometry",
        "quasi_static",
    )


def assemble_planar_truss(
    nodes_m: Sequence[Point2D],
    elements: Sequence[TrussElement],
) -> tuple[tuple[Scalar, ...], ...]:
    nodes = tuple((float(x), float(y)) for x, y in nodes_m)
    if len(nodes) < 2:
        raise ValueError("Treliça precisa de ao menos dois nós")
    if any(not math.isfinite(x) or not math.isfinite(y) for x, y in nodes):
        raise ValueError("Coordenadas dos nós precisam ser finitas")
    elements = tuple(elements)
    if not elements:
        raise ValueError("Treliça precisa de ao menos um elemento")
    ndof = 2 * len(nodes)
    matrix: list[list[Scalar]] = [[0.0 for _ in range(ndof)] for _ in range(ndof)]

    for element in elements:
        if not (0 <= element.node_i < len(nodes) and 0 <= element.node_j < len(nodes)):
            raise ValueError("Elemento referencia nó inexistente")
        xi, yi = nodes[element.node_i]
        xj, yj = nodes[element.node_j]
        dx, dy = xj - xi, yj - yi
        length = math.hypot(dx, dy)
        if length <= 1e-15:
            raise ValueError("Elemento com comprimento nulo")
        c, s = dx / length, dy / length
        scale = element.young_pa * element.area_m2 / length
        local = (
            ( c*c,  c*s, -c*c, -c*s),
            ( c*s,  s*s, -c*s, -s*s),
            (-c*c, -c*s,  c*c,  c*s),
            (-c*s, -s*s,  c*s,  s*s),
        )
        dofs = (
            2 * element.node_i,
            2 * element.node_i + 1,
            2 * element.node_j,
            2 * element.node_j + 1,
        )
        for a in range(4):
            for b in range(4):
                row, col = dofs[a], dofs[b]
                matrix[row][col] = matrix[row][col] + scale * local[a][b]
    return tuple(tuple(row) for row in matrix)


def solve_planar_truss(
    nodes_m: Sequence[Point2D],
    elements: Sequence[TrussElement],
    loads_n: Sequence[tuple[Scalar, Scalar]],
    fixed_dofs: Sequence[int],
) -> PlanarTrussResult:
    nodes = tuple((float(x), float(y)) for x, y in nodes_m)
    elements = tuple(elements)
    loads = tuple(tuple(load) for load in loads_n)
    if len(loads) != len(nodes):
        raise ValueError("loads_n precisa fornecer (Fx,Fy) para cada nó")
    if any(len(load) != 2 for load in loads):
        raise ValueError("Cada carga nodal precisa de duas componentes")
    if any(not math.isfinite(_value(value)) for load in loads for value in load):
        raise ValueError("Carga nodal contém valor não finito")

    stiffness = assemble_planar_truss(nodes, elements)
    ndof = 2 * len(nodes)
    fixed = tuple(sorted(set(fixed_dofs)))
    if any(isinstance(dof, bool) or not isinstance(dof, int) or not 0 <= dof < ndof for dof in fixed):
        raise ValueError("fixed_dofs contém índice inválido")
    if not fixed:
        raise ValueError("Treliça precisa de vínculos para eliminar modos rígidos")
    free = tuple(dof for dof in range(ndof) if dof not in fixed)
    if not free:
        raise ValueError("Treliça não possui grau de liberdade livre")

    load_vector: tuple[Scalar, ...] = tuple(value for load in loads for value in load)
    reduced_matrix = tuple(
        tuple(stiffness[row][col] for col in free)
        for row in free
    )
    reduced_rhs = tuple(load_vector[row] for row in free)
    free_solution = solve_linear_system(reduced_matrix, reduced_rhs)

    displacement: list[Scalar] = [0.0] * ndof
    for dof, value in zip(free, free_solution):
        displacement[dof] = value

    reactions: list[Scalar] = []
    for row in range(ndof):
        internal: Scalar = 0.0
        for col in range(ndof):
            internal = internal + stiffness[row][col] * displacement[col]
        reactions.append(internal - load_vector[row])

    strains: list[Scalar] = []
    stresses: list[Scalar] = []
    forces: list[Scalar] = []
    for element in elements:
        xi, yi = nodes[element.node_i]
        xj, yj = nodes[element.node_j]
        dx, dy = xj - xi, yj - yi
        length = math.hypot(dx, dy)
        c, s = dx / length, dy / length
        ui = displacement[2 * element.node_i]
        vi = displacement[2 * element.node_i + 1]
        uj = displacement[2 * element.node_j]
        vj = displacement[2 * element.node_j + 1]
        extension = c * (uj - ui) + s * (vj - vi)
        strain = extension / length
        stress = element.young_pa * strain
        force = element.area_m2 * stress
        strains.append(strain)
        stresses.append(stress)
        forces.append(force)

    compliance: Scalar = 0.0
    for dof in range(ndof):
        compliance = compliance + load_vector[dof] * displacement[dof]

    paired_displacements = tuple(
        (displacement[2 * node], displacement[2 * node + 1])
        for node in range(len(nodes))
    )
    paired_reactions = tuple(
        (reactions[2 * node], reactions[2 * node + 1])
        for node in range(len(nodes))
    )
    return PlanarTrussResult(
        paired_displacements,
        paired_reactions,
        tuple(strains),
        tuple(stresses),
        tuple(forces),
        compliance,
    )


__all__ = [
    "Scalar", "Point2D", "TrussElement", "PlanarTrussResult",
    "assemble_planar_truss", "solve_planar_truss",
]
