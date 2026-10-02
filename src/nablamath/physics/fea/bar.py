"""Differentiable 1D axial-bar finite element reference solver."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence, TypeAlias

from ...autodiff import Var

Scalar: TypeAlias = float | Var


def _value(x: Scalar) -> float:
    return x.value if isinstance(x, Var) else float(x)


def solve_linear_system(matrix: Sequence[Sequence[Scalar]], rhs: Sequence[Scalar]) -> tuple[Scalar, ...]:
    """Gaussian elimination with primal-value pivoting; arithmetic remains differentiable."""
    n = len(rhs)
    if n == 0 or len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("Sistema linear precisa ser quadrado e não vazio")
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(_value(a[row][column])))
        if abs(_value(a[pivot][column])) <= 1e-30:
            raise ValueError("Matriz singular ou mal condicionada no pivô")
        if pivot != column:
            a[column], a[pivot] = a[pivot], a[column]
        pivot_value = a[column][column]
        for row in range(column + 1, n):
            factor = a[row][column] / pivot_value
            for j in range(column, n + 1):
                a[row][j] = a[row][j] - factor * a[column][j]
    x: list[Scalar] = [0.0] * n
    for row in range(n - 1, -1, -1):
        residual: Scalar = a[row][n]
        for j in range(row + 1, n):
            residual = residual - a[row][j] * x[j]
        x[row] = residual / a[row][row]
    return tuple(x)


def assemble_uniform_bar(
    length_m: float, area_m2: Scalar, young_pa: Scalar, elements: int
) -> tuple[tuple[Scalar, ...], ...]:
    if not math.isfinite(length_m) or length_m <= 0:
        raise ValueError("Comprimento deve ser positivo e finito")
    if isinstance(elements, bool) or not isinstance(elements, int) or not 1 <= elements <= 10000:
        raise ValueError("elements deve ser inteiro entre 1 e 10000")
    if _value(area_m2) <= 0 or _value(young_pa) <= 0:
        raise ValueError("Área e módulo de Young devem ser positivos")
    size = elements + 1
    matrix: list[list[Scalar]] = [[0.0 for _ in range(size)] for _ in range(size)]
    element_length = length_m / elements
    stiffness = young_pa * area_m2 / element_length
    for element in range(elements):
        i, j = element, element + 1
        matrix[i][i] = matrix[i][i] + stiffness
        matrix[i][j] = matrix[i][j] - stiffness
        matrix[j][i] = matrix[j][i] - stiffness
        matrix[j][j] = matrix[j][j] + stiffness
    return tuple(tuple(row) for row in matrix)


@dataclass(frozen=True)
class AxialBarResult:
    displacements_m: tuple[Scalar, ...]
    end_displacement_m: Scalar
    element_strain: tuple[Scalar, ...]
    element_stress_pa: tuple[Scalar, ...]
    assumptions: tuple[str, ...] = (
        "linear_elastic", "small_strain", "one_dimensional_axial",
        "uniform_material", "uniform_area", "left_node_fixed",
    )


def solve_uniform_axial_bar(length_m: float, area_m2: Scalar, young_pa: Scalar,
                            end_force_n: Scalar, elements: int = 8) -> AxialBarResult:
    """Linear 1D FEA with node 0 fixed and an axial force at the final node."""
    stiffness = assemble_uniform_bar(length_m, area_m2, young_pa, elements)
    reduced = tuple(tuple(stiffness[i][j] for j in range(1, elements + 1))
                    for i in range(1, elements + 1))
    loads: list[Scalar] = [0.0 for _ in range(elements)]
    loads[-1] = end_force_n
    free = solve_linear_system(reduced, loads)
    displacements: tuple[Scalar, ...] = (0.0,) + free
    element_length = length_m / elements
    strain = tuple((displacements[i + 1] - displacements[i]) / element_length for i in range(elements))
    stress = tuple(young_pa * item for item in strain)
    return AxialBarResult(displacements, displacements[-1], strain, stress)


@dataclass(frozen=True)
class BarSensitivity:
    end_displacement_m: float
    d_displacement_d_young: float
    d_displacement_d_area: float


def bar_end_sensitivity(length_m: float, area_m2: float, young_pa: float,
                        end_force_n: float, elements: int = 8) -> BarSensitivity:
    area = Var(area_m2)
    young = Var(young_pa)
    result = solve_uniform_axial_bar(length_m, area, young, end_force_n, elements)
    if not isinstance(result.end_displacement_m, Var):
        raise RuntimeError("FEA diferenciável perdeu o grafo de autodiff")
    result.end_displacement_m.backward()
    return BarSensitivity(result.end_displacement_m.value, young.grad, area.grad)


__all__ = [
    "Scalar", "solve_linear_system", "assemble_uniform_bar", "AxialBarResult",
    "solve_uniform_axial_bar", "BarSensitivity", "bar_end_sensitivity",
]