"""Polinômios univariados exatos sobre os racionais."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class Polynomial:
    coefficients: tuple[Fraction, ...]  # ordem crescente

    def __post_init__(self) -> None:
        values = [Fraction(value) for value in self.coefficients]
        if not values: values = [Fraction()]
        while len(values) > 1 and values[-1] == 0: values.pop()
        object.__setattr__(self, "coefficients", tuple(values))

    @property
    def degree(self) -> int: return -1 if self.is_zero else len(self.coefficients) - 1
    @property
    def is_zero(self) -> bool: return self.coefficients == (0,)
    @property
    def leading(self) -> Fraction: return self.coefficients[-1]

    def __call__(self, value: int | Fraction) -> Fraction:
        x = Fraction(value); result = Fraction()
        for coefficient in reversed(self.coefficients): result = result * x + coefficient
        return result

    def __add__(self, other: "Polynomial") -> "Polynomial":
        size = max(len(self.coefficients), len(other.coefficients))
        return Polynomial(tuple((self.coefficients[i] if i < len(self.coefficients) else 0) +
                                (other.coefficients[i] if i < len(other.coefficients) else 0) for i in range(size)))

    def __sub__(self, other: "Polynomial") -> "Polynomial":
        return self + Polynomial(tuple(-value for value in other.coefficients))

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        result = [Fraction()] * (len(self.coefficients) + len(other.coefficients) - 1)
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients): result[i + j] += left * right
        return Polynomial(tuple(result))

    def derivative(self) -> "Polynomial":
        return Polynomial(tuple(index * value for index, value in enumerate(self.coefficients))[1:])

    def divmod(self, divisor: "Polynomial") -> tuple["Polynomial", "Polynomial"]:
        if divisor.is_zero: raise ZeroDivisionError("divisão por polinômio zero")
        remainder = self; quotient = [Fraction()] * max(1, self.degree - divisor.degree + 1)
        while not remainder.is_zero and remainder.degree >= divisor.degree:
            degree = remainder.degree - divisor.degree; coefficient = remainder.leading / divisor.leading
            quotient[degree] = coefficient
            term = Polynomial((Fraction(),) * degree + (coefficient,))
            remainder = remainder - term * divisor
        return Polynomial(tuple(quotient)), remainder

    def monic(self) -> "Polynomial":
        if self.is_zero: return self
        return Polynomial(tuple(value / self.leading for value in self.coefficients))


def polynomial_gcd(left: Polynomial, right: Polynomial) -> Polynomial:
    while not right.is_zero:
        _, remainder = left.divmod(right); left, right = right, remainder
    return left.monic()


__all__ = ["Polynomial", "polynomial_gcd"]
