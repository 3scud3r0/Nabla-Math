"""Interpolação polinomial exata sobre os racionais."""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable

from .univariate import Polynomial


Point = tuple[Fraction, Fraction]


def _normalize_points(points: Iterable[tuple[int | Fraction, int | Fraction]]) -> tuple[Point, ...]:
    normalized = tuple((Fraction(x), Fraction(y)) for x, y in points)
    if not normalized:
        raise ValueError("ao menos um ponto é obrigatório")
    if len(normalized) > 10_000:
        raise ValueError("quantidade de pontos excede o limite")
    xs = tuple(x for x, _ in normalized)
    if len(set(xs)) != len(xs):
        raise ValueError("abscissas devem ser distintas")
    return normalized


def lagrange(points: Iterable[tuple[int | Fraction, int | Fraction]]) -> Polynomial:
    """Constrói o único polinômio de grau menor que ``len(points)``."""
    normalized = _normalize_points(points)
    result = Polynomial((0,))
    variable = Polynomial((0, 1))
    for index, (x_value, y_value) in enumerate(normalized):
        basis = Polynomial((1,))
        denominator = Fraction(1)
        for other_index, (other_x, _) in enumerate(normalized):
            if index == other_index:
                continue
            basis = basis * (variable - Polynomial((other_x,)))
            denominator *= x_value - other_x
        result = result + basis * Polynomial((y_value / denominator,))
    return result


def divided_differences(
    points: Iterable[tuple[int | Fraction, int | Fraction]],
) -> tuple[Fraction, ...]:
    """Retorna coeficientes da forma de Newton para pontos distintos."""
    normalized = _normalize_points(points)
    coefficients = [y for _, y in normalized]
    result = [coefficients[0]]
    for order in range(1, len(normalized)):
        coefficients = [
            (coefficients[index + 1] - coefficients[index])
            / (normalized[index + order][0] - normalized[index][0])
            for index in range(len(coefficients) - 1)
        ]
        result.append(coefficients[0])
    return tuple(result)


def newton_interpolation(
    points: Iterable[tuple[int | Fraction, int | Fraction]],
) -> Polynomial:
    """Constrói o interpolante usando diferenças divididas de Newton."""
    normalized = _normalize_points(points)
    coefficients = divided_differences(normalized)
    result = Polynomial((coefficients[0],))
    product = Polynomial((1,))
    variable = Polynomial((0, 1))
    for index in range(1, len(coefficients)):
        product = product * (variable - Polynomial((normalized[index - 1][0],)))
        result = result + product * Polynomial((coefficients[index],))
    return result


def finite_differences(values: Iterable[int | Fraction]) -> tuple[tuple[Fraction, ...], ...]:
    """Cria a tabela triangular de diferenças finitas."""
    row = tuple(Fraction(value) for value in values)
    if not row:
        raise ValueError("valores vazios")
    table = [row]
    while len(row) > 1:
        row = tuple(right - left for left, right in zip(row, row[1:]))
        table.append(row)
    return tuple(table)


__all__ = ["divided_differences", "finite_differences", "lagrange", "newton_interpolation"]
