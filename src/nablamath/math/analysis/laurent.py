"""Exact Laurent coefficients and residues of rational functions at rational points."""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from ...expression import Expr
from ..algebra.groebner import Polynomial, polynomial_from_expr


@dataclass(frozen=True)
class LaurentSeries:
    center: Fraction
    coefficients: tuple[tuple[int, Fraction], ...]
    pole_order: int
    truncation_order: int

    def coefficient(self, exponent: int) -> Fraction:
        return dict(self.coefficients).get(exponent, Fraction(0))

    @property
    def residue(self) -> Fraction:
        return self.coefficient(-1)


def _shift(polynomial: Polynomial, center: Fraction) -> list[Fraction]:
    maximum = max((monomial[0] for monomial, _ in polynomial.terms), default=0)
    result = [Fraction(0)] * (maximum + 1)
    for (degree,), coefficient in polynomial.terms:
        for power in range(degree + 1):
            result[power] += coefficient * comb(degree, power) * center ** (degree - power)
    return result


def rational_laurent_series(numerator: Expr, denominator: Expr, variable: str,
                            center: Fraction | int, *, order: int = 8) -> LaurentSeries:
    if type(order) is not int or not 0 <= order <= 128:
        raise ValueError("order deve estar entre 0 e 128")
    point = Fraction(center)
    top = _shift(polynomial_from_expr(numerator, (variable,)), point)
    bottom = _shift(polynomial_from_expr(denominator, (variable,)), point)
    top_start = next((index for index, value in enumerate(top) if value), None)
    bottom_start = next((index for index, value in enumerate(bottom) if value), None)
    if bottom_start is None:
        raise ZeroDivisionError("Denominador identicamente zero")
    if top_start is None:
        return LaurentSeries(point, (), 0, order)
    top, bottom = top[top_start:], bottom[bottom_start:]
    shift = top_start - bottom_start
    count = max(0, order - shift + 1)
    quotient: list[Fraction] = []
    for degree in range(count):
        target = top[degree] if degree < len(top) else Fraction(0)
        correction = sum((bottom[index] if index < len(bottom) else 0)
                         * quotient[degree - index] for index in range(1, degree + 1))
        quotient.append((target - correction) / bottom[0])
    coefficients = tuple((shift + index, value) for index, value in enumerate(quotient) if value)
    return LaurentSeries(point, coefficients, max(0, -shift), order)


def rational_residue(numerator: Expr, denominator: Expr, variable: str,
                     center: Fraction | int) -> Fraction:
    return rational_laurent_series(numerator, denominator, variable, center, order=0).residue


__all__ = ["LaurentSeries", "rational_laurent_series", "rational_residue"]
