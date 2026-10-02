"""Corpos finitos explícitos derivados de anéis finitos validados."""

from dataclasses import dataclass
from itertools import product
from typing import Generic, TypeVar

from .rings import FiniteRing, integers_modulo
from ..number_theory.elementary import is_prime

T = TypeVar("T")


@dataclass(frozen=True)
class FiniteField(Generic[T]):
    ring: FiniteRing[T]

    def __post_init__(self) -> None:
        for left, right in product(self.ring.elements, repeat=2):
            if self.ring.multiply(left, right) != self.ring.multiply(right, left): raise ValueError("multiplicação não comutativa")
        if set(self.ring.units()) != set(self.ring.elements) - {self.ring.zero}:
            raise ValueError("todo elemento não nulo precisa ser invertível")

    def inverse(self, value: T) -> T:
        if value == self.ring.zero: raise ZeroDivisionError("zero não possui inverso")
        for candidate in self.ring.elements:
            if self.ring.multiply(value, candidate) == self.ring.one: return candidate
        raise AssertionError("corpo validado sem inverso")

    def divide(self, numerator: T, denominator: T) -> T:
        return self.ring.multiply(numerator, self.inverse(denominator))


def prime_field(characteristic: int) -> FiniteField[int]:
    if not is_prime(characteristic): raise ValueError("característica deve ser prima")
    return FiniteField(integers_modulo(characteristic))


__all__ = ["FiniteField", "prime_field"]
