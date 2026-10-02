"""Exact finite-point limits and Taylor jets for rational-expression ASTs."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import factorial

from ..expression import Binary, Expr, Number, Symbol, evaluate
from ..math.algebra.groebner import Polynomial, polynomial_from_expr
from .differentiate import differentiate


@dataclass(frozen=True)
class TaylorSeries:
    variable: str
    center: Fraction
    coefficients: tuple[Fraction, ...]
    polynomial: Expr
    remainder_order: int


@dataclass(frozen=True)
class RationalLimit:
    status: str
    value: Fraction | None
    numerator_order: int
    denominator_order: int


def _build_taylor(variable: str, center: Fraction,
                  coefficients: tuple[Fraction, ...]) -> Expr:
    result: Expr = Number(Fraction(0))
    offset: Expr = Binary("-", Symbol(variable), Number(center))
    for exponent, coefficient in enumerate(coefficients):
        term: Expr = Number(coefficient)
        if exponent:
            term = Binary("*", term, Binary("**", offset, Number(Fraction(exponent))))
        result = Binary("+", result, term)
    return result


def taylor_series(expr: Expr, variable: str, center: Fraction | int,
                  order: int) -> TaylorSeries:
    if type(order) is not int or not 0 <= order <= 32:
        raise ValueError("order deve estar entre 0 e 32")
    point = Fraction(center)
    current = expr
    coefficients = []
    for exponent in range(order + 1):
        coefficients.append(evaluate(current, {variable: point}) / factorial(exponent))
        if exponent < order:
            current = differentiate(current, variable).derivative
    values = tuple(coefficients)
    return TaylorSeries(variable, point, values, _build_taylor(variable, point, values), order + 1)


def _multiplicity(polynomial: Polynomial, point: Fraction) -> tuple[int, Polynomial]:
    multiplicity, current = 0, polynomial
    while not current.is_zero and current.evaluate({polynomial.variables[0]: point}) == 0:
        # Univariate synthetic division, exact because point is a root.
        maximum = max(monomial[0] for monomial, _ in current.terms)
        term_map = dict(current.terms)
        dense = [term_map.get((degree,), Fraction(0)) for degree in range(maximum + 1)]
        quotient_high = [dense[-1]]
        for coefficient in reversed(dense[1:-1]):
            quotient_high.append(coefficient + point * quotient_high[-1])
        remainder = dense[0] + point * quotient_high[-1]
        if remainder:
            break
        quotient = {((maximum - 1 - index),): value
                    for index, value in enumerate(quotient_high) if value}
        current = Polynomial(polynomial.variables, quotient)
        multiplicity += 1
    return multiplicity, current


def rational_limit(numerator: Expr, denominator: Expr, variable: str,
                   point: Fraction | int) -> RationalLimit:
    center = Fraction(point)
    top = polynomial_from_expr(numerator, (variable,))
    bottom = polynomial_from_expr(denominator, (variable,))
    if bottom.is_zero:
        return RationalLimit("undefined", None, 0, 0)
    top_order, reduced_top = _multiplicity(top, center)
    bottom_order, reduced_bottom = _multiplicity(bottom, center)
    if top.is_zero:
        return RationalLimit("finite", Fraction(0), top_order, bottom_order)
    if top_order < bottom_order:
        return RationalLimit("infinite_or_sided", None, top_order, bottom_order)
    top_value = reduced_top.evaluate({variable: center})
    bottom_value = reduced_bottom.evaluate({variable: center})
    if bottom_value == 0:
        raise ArithmeticError("Cancelamento de multiplicidade falhou")
    value = Fraction(0) if top_order > bottom_order else top_value / bottom_value
    return RationalLimit("finite", value, top_order, bottom_order)


__all__ = ["RationalLimit", "TaylorSeries", "rational_limit", "taylor_series"]
