"""Regressão linear simples exata e diagnósticos racionais."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .descriptive import mean


@dataclass(frozen=True)
class LinearFit:
    intercept: Fraction
    slope: Fraction
    residual_sum_squares: Fraction
    sample_size: int

    def predict(self, value: int | Fraction) -> Fraction:
        return self.intercept + self.slope * Fraction(value)


def linear_regression(x_values: Iterable[int | Fraction], y_values: Iterable[int | Fraction]) -> LinearFit:
    x = tuple(Fraction(value) for value in x_values); y = tuple(Fraction(value) for value in y_values)
    if len(x) != len(y) or len(x) < 2: raise ValueError("regressão requer ao menos dois pares")
    x_mean, y_mean = mean(x), mean(y)
    denominator = sum(((value - x_mean) ** 2 for value in x), Fraction())
    if denominator == 0: raise ValueError("preditor constante não identifica inclinação")
    slope = sum(((a - x_mean) * (b - y_mean) for a, b in zip(x, y, strict=True)), Fraction()) / denominator
    intercept = y_mean - slope * x_mean
    residual = sum(((b - (intercept + slope * a)) ** 2 for a, b in zip(x, y, strict=True)), Fraction())
    return LinearFit(intercept, slope, residual, len(x))


__all__ = ["LinearFit", "linear_regression"]
