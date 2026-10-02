"""Finite simplicial complexes, rational homology and 1D fundamental groups."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Hashable, Iterable

Vertex = Hashable
Simplex = tuple[Vertex, ...]


def _rank(matrix: list[list[Fraction]], columns: int) -> int:
    rows = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(columns):
        candidate = next((index for index in range(pivot_row, len(rows)) if rows[index][column]), None)
        if candidate is None:
            continue
        rows[pivot_row], rows[candidate] = rows[candidate], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for index, row in enumerate(rows):
            if index != pivot_row and row[column]:
                factor = row[column]
                rows[index] = [value - factor * pivot for value, pivot in zip(row, rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


@dataclass(frozen=True)
class SimplicialComplex:
    simplices: frozenset[Simplex]

    def __init__(self, maximal_simplices: Iterable[Iterable[Vertex]]) -> None:
        closure: set[Simplex] = set()
        for raw in maximal_simplices:
            simplex = tuple(sorted(set(raw), key=repr))
            if not simplex:
                raise ValueError("Simplexo vazio não é uma célula deste modelo")
            for size in range(1, len(simplex) + 1):
                closure.update(combinations(simplex, size))
        object.__setattr__(self, "simplices", frozenset(closure))

    @property
    def dimension(self) -> int:
        return max((len(simplex) - 1 for simplex in self.simplices), default=-1)

    def cells(self, dimension: int) -> tuple[Simplex, ...]:
        return tuple(sorted((simplex for simplex in self.simplices
                            if len(simplex) == dimension + 1), key=repr))

    def boundary_matrix(self, dimension: int) -> tuple[tuple[Fraction, ...], ...]:
        if dimension < 1:
            return ()
        sources, targets = self.cells(dimension), self.cells(dimension - 1)
        target_index = {simplex: index for index, simplex in enumerate(targets)}
        matrix = [[Fraction(0) for _ in sources] for _ in targets]
        for column, simplex in enumerate(sources):
            for removed in range(len(simplex)):
                face = simplex[:removed] + simplex[removed + 1:]
                matrix[target_index[face]][column] = Fraction((-1) ** removed)
        return tuple(tuple(row) for row in matrix)

    def boundary_rank(self, dimension: int) -> int:
        return _rank([list(row) for row in self.boundary_matrix(dimension)],
                     len(self.cells(dimension)))

    def betti_number(self, dimension: int) -> int:
        if dimension < 0:
            raise ValueError("Dimensão deve ser não negativa")
        return len(self.cells(dimension)) - self.boundary_rank(dimension) - self.boundary_rank(dimension + 1)

    def betti_numbers(self) -> tuple[int, ...]:
        return tuple(self.betti_number(index) for index in range(self.dimension + 1))

    def verify_boundary_squared_zero(self) -> bool:
        for dimension in range(2, self.dimension + 1):
            lower, upper = self.boundary_matrix(dimension - 1), self.boundary_matrix(dimension)
            if not lower or not upper:
                continue
            for row in range(len(lower)):
                for column in range(len(upper[0])):
                    if sum(lower[row][middle] * upper[middle][column]
                           for middle in range(len(upper))):
                        return False
        return True

    def fundamental_group_rank_1d(self) -> int:
        if self.dimension > 1:
            raise ValueError("π1 geral de complexos 2D+ não é implementado")
        vertices = self.cells(0)
        adjacency = {vertex: set() for vertex in vertices}
        for edge in self.cells(1):
            left, right = (edge[0],), (edge[1],)
            adjacency[left].add(right)
            adjacency[right].add(left)
        components, unseen = 0, set(vertices)
        while unseen:
            components += 1
            stack = [unseen.pop()]
            while stack:
                neighbors = adjacency[stack.pop()] & unseen
                unseen.difference_update(neighbors)
                stack.extend(neighbors)
        return len(self.cells(1)) - len(vertices) + components


__all__ = ["Simplex", "SimplicialComplex", "Vertex"]
