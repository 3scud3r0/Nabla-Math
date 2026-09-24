"""Dimensões SI e quantidades exatas; sem coerção silenciosa entre unidades."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Unit:
    """Dimensão (massa, comprimento, tempo) e escala racional frente ao SI."""

    dimensions: tuple[int, int, int] = (0, 0, 0)
    scale: Fraction = Fraction(1)
    symbol: str = "1"

    def __post_init__(self) -> None:
        if len(self.dimensions) != 3 or any(type(x) is not int for x in self.dimensions):
            raise ValueError("Dimensão SI inválida")
        if self.scale <= 0:
            raise ValueError("Escala de unidade precisa ser positiva")

    def __mul__(self, other: Unit) -> Unit:
        return Unit(tuple(a+b for a,b in zip(self.dimensions, other.dimensions)),
                    self.scale*other.scale, f"({self.symbol}*{other.symbol})")

    def __truediv__(self, other: Unit) -> Unit:
        return Unit(tuple(a-b for a,b in zip(self.dimensions, other.dimensions)),
                    self.scale/other.scale, f"({self.symbol}/{other.symbol})")

    def __pow__(self, exponent: int) -> Unit:
        if type(exponent) is not int:
            raise ValueError("Expoente dimensional precisa ser inteiro")
        return Unit(tuple(a*exponent for a in self.dimensions),
                    self.scale**exponent, f"({self.symbol}^{exponent})")


METER = Unit((0, 1, 0), Fraction(1), "m")
SECOND = Unit((0, 0, 1), Fraction(1), "s")
KILOGRAM = Unit((1, 0, 0), Fraction(1), "kg")
KILOMETER = Unit((0, 1, 0), Fraction(1000), "km")
HOUR = Unit((0, 0, 1), Fraction(3600), "h")
ONE = Unit()


@dataclass(frozen=True)
class Quantity:
    value: Fraction
    unit: Unit = ONE

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", Fraction(self.value))

    def to(self, unit: Unit) -> Quantity:
        if self.unit.dimensions != unit.dimensions:
            raise ValueError("Conversão entre dimensões incompatíveis")
        return Quantity(self.value * self.unit.scale / unit.scale, unit)

    def __add__(self, other: Quantity) -> Quantity:
        return Quantity(self.value + other.to(self.unit).value, self.unit)

    def __sub__(self, other: Quantity) -> Quantity:
        return Quantity(self.value - other.to(self.unit).value, self.unit)

    def __mul__(self, other: Quantity) -> Quantity:
        return Quantity(self.value * other.value, self.unit * other.unit)

    def __truediv__(self, other: Quantity) -> Quantity:
        if other.value == 0:
            raise ZeroDivisionError("Divisão por quantidade zero")
        return Quantity(self.value / other.value, self.unit / other.unit)
