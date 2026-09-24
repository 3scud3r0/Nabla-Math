"""Eliminação gaussiana exata com pivotamento por entrada não nula."""

from fractions import Fraction
from typing import Sequence


def solve_exact(matrix: Sequence[Sequence[int | Fraction]],
                rhs: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    """Resolve Ax=b sobre ℚ; singularidade é erro, sem arredondamento."""
    n = len(rhs)
    if n == 0 or len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("Matriz precisa ser quadrada e não vazia")
    data = [[Fraction(v) for v in row] + [Fraction(rhs[i])]
            for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((row for row in range(col, n) if data[row][col] != 0), None)
        if pivot is None:
            raise ValueError("Sistema singular ou sem solução única")
        data[col], data[pivot] = data[pivot], data[col]
        factor = data[col][col]
        data[col] = [v / factor for v in data[col]]
        for row in range(n):
            if row != col:
                factor = data[row][col]
                data[row] = [a - factor*b for a,b in zip(data[row], data[col])]
    return tuple(row[-1] for row in data)
