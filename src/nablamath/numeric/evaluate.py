"""Valor exato e aproximação float rotulada com erro de representação."""

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, nextafter
from typing import Mapping

from ..expression import Expr, evaluate


@dataclass(frozen=True)
class Approximation:
    exact: Fraction
    floating: float
    representation_error: Fraction


def evaluate_with_error(expr: Expr, values: Mapping[str, Fraction]) -> Approximation:
    exact = evaluate(expr, values)
    number = float(exact)
    if not isfinite(number):
        raise OverflowError("Resultado racional não cabe em float finito")
    error = abs(Fraction.from_float(number) - exact)
    return Approximation(exact, number, error)
