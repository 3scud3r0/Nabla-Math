"""Matrizes densas exatas sobre os racionais."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class Matrix:
    rows: tuple[tuple[Fraction, ...], ...]

    def __post_init__(self) -> None:
        converted = tuple(tuple(Fraction(value) for value in row) for row in self.rows)
        if not converted or not converted[0] or any(len(row) != len(converted[0]) for row in converted):
            raise ValueError("matriz deve ser retangular e não vazia")
        object.__setattr__(self, "rows", converted)

    @property
    def shape(self) -> tuple[int, int]: return len(self.rows), len(self.rows[0])

    def transpose(self) -> "Matrix": return Matrix(tuple(zip(*self.rows)))

    def __matmul__(self, other: "Matrix") -> "Matrix":
        if self.shape[1] != other.shape[0]: raise ValueError("dimensões incompatíveis")
        columns = other.transpose().rows
        return Matrix(tuple(tuple(sum((a * b for a, b in zip(row, column, strict=True)), Fraction())
                                  for column in columns) for row in self.rows))

    def echelon(self) -> tuple["Matrix", int]:
        data = [list(row) for row in self.rows]; row = 0; rank = 0
        for column in range(self.shape[1]):
            pivot = next((candidate for candidate in range(row, self.shape[0]) if data[candidate][column]), None)
            if pivot is None: continue
            data[row], data[pivot] = data[pivot], data[row]
            scale = data[row][column]; data[row] = [value / scale for value in data[row]]
            for candidate in range(self.shape[0]):
                if candidate != row and data[candidate][column]:
                    factor = data[candidate][column]
                    data[candidate] = [value - factor * base for value, base in zip(data[candidate], data[row], strict=True)]
            row += 1; rank += 1
            if row == self.shape[0]: break
        return Matrix(tuple(tuple(values) for values in data)), rank

    def determinant(self) -> Fraction:
        if self.shape[0] != self.shape[1]: raise ValueError("determinante requer matriz quadrada")
        data = [list(row) for row in self.rows]; result = Fraction(1)
        for column in range(self.shape[0]):
            pivot = next((row for row in range(column, self.shape[0]) if data[row][column]), None)
            if pivot is None: return Fraction()
            if pivot != column: data[column], data[pivot] = data[pivot], data[column]; result = -result
            value = data[column][column]; result *= value
            for row in range(column + 1, self.shape[0]):
                factor = data[row][column] / value
                for index in range(column, self.shape[1]): data[row][index] -= factor * data[column][index]
        return result

    def inverse(self) -> "Matrix":
        if self.shape[0] != self.shape[1]: raise ValueError("inversa requer matriz quadrada")
        size = self.shape[0]
        data = [list(row) + list(identity(size).rows[index]) for index, row in enumerate(self.rows)]
        for column in range(size):
            pivot = next((row for row in range(column, size) if data[row][column]), None)
            if pivot is None: raise ValueError("matriz singular")
            data[column], data[pivot] = data[pivot], data[column]
            scale = data[column][column]; data[column] = [value / scale for value in data[column]]
            for row in range(size):
                if row != column and data[row][column]:
                    factor = data[row][column]
                    data[row] = [value - factor * base for value, base in zip(data[row], data[column], strict=True)]
        return Matrix(tuple(tuple(row[size:]) for row in data))


def identity(size: int) -> Matrix:
    if not 1 <= size <= 10_000: raise ValueError("dimensão inválida")
    return Matrix(tuple(tuple(Fraction(index == column) for column in range(size)) for index in range(size)))


__all__ = ["Matrix", "identity"]
