"""Programação linear bidimensional exata por enumeração de vértices."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations


@dataclass(frozen=True)
class Constraint2:
    a: Fraction
    b: Fraction
    upper: Fraction
    def __post_init__(self) -> None:
        object.__setattr__(self, "a", Fraction(self.a)); object.__setattr__(self, "b", Fraction(self.b)); object.__setattr__(self, "upper", Fraction(self.upper))
        if self.a == 0 and self.b == 0: raise ValueError("restrição degenerada")
    def holds(self, point: tuple[Fraction, Fraction]) -> bool: return self.a * point[0] + self.b * point[1] <= self.upper


def maximize_2d(objective: tuple[int | Fraction, int | Fraction], constraints: tuple[Constraint2, ...], *,
                x_bounds: tuple[int | Fraction, int | Fraction],
                y_bounds: tuple[int | Fraction, int | Fraction]) -> tuple[tuple[Fraction, Fraction], Fraction]:
    c = (Fraction(objective[0]), Fraction(objective[1]))
    xmin, xmax = map(Fraction, x_bounds); ymin, ymax = map(Fraction, y_bounds)
    if xmin > xmax or ymin > ymax: raise ValueError("limites da caixa inválidos")
    boundaries = list(constraints) + [Constraint2(-1, 0, -xmin), Constraint2(1, 0, xmax),
                                      Constraint2(0, -1, -ymin), Constraint2(0, 1, ymax)]
    candidates: set[tuple[Fraction, Fraction]] = set()
    for left, right in combinations(boundaries, 2):
        determinant = left.a * right.b - right.a * left.b
        if determinant == 0: continue
        x = (left.upper * right.b - right.upper * left.b) / determinant
        y = (left.a * right.upper - right.a * left.upper) / determinant
        point = (x, y)
        if all(constraint.holds(point) for constraint in boundaries): candidates.add(point)
    if not candidates: raise ValueError("região viável vazia ou sem vértices detectáveis")
    scored = sorted(((c[0] * x + c[1] * y, x, y) for x, y in candidates), key=lambda row: (row[0], -row[1], -row[2]))
    value, x, y = scored[-1]
    return (x, y), value


__all__ = ["Constraint2", "maximize_2d"]
