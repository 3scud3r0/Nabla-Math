"""Elliptic-curve group arithmetic over prime fields (not a crypto protocol)."""

from __future__ import annotations
from dataclasses import dataclass
from .primality import miller_rabin

Point = tuple[int, int] | None


@dataclass(frozen=True)
class EllipticCurveFp:
    prime: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if not 2 <= self.prime < 2**64 or not miller_rabin(self.prime):
            raise ValueError("O módulo da curva deve ser primo de até 64 bits")
        object.__setattr__(self, "a", self.a % self.prime)
        object.__setattr__(self, "b", self.b % self.prime)
        if (4 * self.a**3 + 27 * self.b**2) % self.prime == 0:
            raise ValueError("Curva singular")

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - x**3 - self.a * x - self.b) % self.prime == 0

    def negate(self, point: Point) -> Point:
        if not self.contains(point):
            raise ValueError("Ponto fora da curva")
        return None if point is None else (point[0] % self.prime, -point[1] % self.prime)

    def add(self, first: Point, second: Point) -> Point:
        if not self.contains(first) or not self.contains(second):
            raise ValueError("Ponto fora da curva")
        if first is None:
            return second
        if second is None:
            return first
        x1, y1 = first[0] % self.prime, first[1] % self.prime
        x2, y2 = second[0] % self.prime, second[1] % self.prime
        if x1 == x2 and (y1 + y2) % self.prime == 0:
            return None
        slope = ((3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.prime)
                 if first == second else (y2 - y1) * pow(x2 - x1, -1, self.prime)) % self.prime
        x3 = (slope * slope - x1 - x2) % self.prime
        result = (x3, (slope * (x1 - x3) - y1) % self.prime)
        if not self.contains(result):
            raise ArithmeticError("Lei de grupo produziu ponto inválido")
        return result

    def multiply(self, scalar: int, point: Point) -> Point:
        if type(scalar) is not int:
            raise ValueError("Escalar deve ser inteiro")
        if scalar < 0:
            return self.multiply(-scalar, self.negate(point))
        result, addend = None, point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            addend, scalar = self.add(addend, addend), scalar // 2
        return result

    def points(self, *, prime_limit: int = 10_000) -> tuple[Point, ...]:
        if self.prime > prime_limit:
            raise RuntimeError("Enumeração excede limite do corpo")
        return (None, *(point for x in range(self.prime) for y in range(self.prime)
                        if self.contains(point := (x, y))))


__all__ = ["EllipticCurveFp", "Point"]
