"""Anéis finitos unitários por tabelas, verificados exaustivamente."""

from dataclasses import dataclass
from itertools import product
from typing import Generic, Mapping, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class FiniteRing(Generic[T]):
    elements: tuple[T, ...]
    zero: T
    one: T
    addition: Mapping[tuple[T, T], T]
    multiplication: Mapping[tuple[T, T], T]

    def __post_init__(self) -> None:
        values = set(self.elements); pairs = set(product(self.elements, repeat=2))
        if not self.elements or len(values) != len(self.elements) or self.zero not in values or self.one not in values:
            raise ValueError("elementos, zero ou unidade inválidos")
        for table in (self.addition, self.multiplication):
            if set(table) != pairs or any(value not in values for value in table.values()):
                raise ValueError("operação não é total e fechada")
        for a in self.elements:
            if self.add(self.zero, a) != a or self.add(a, self.zero) != a: raise ValueError("zero aditivo inválido")
            if self.multiply(self.one, a) != a or self.multiply(a, self.one) != a: raise ValueError("unidade inválida")
            if not any(self.add(a, b) == self.zero for b in self.elements): raise ValueError("inverso aditivo ausente")
        for a, b in pairs:
            if self.add(a, b) != self.add(b, a): raise ValueError("adição não comutativa")
        for a, b, c in product(self.elements, repeat=3):
            if self.add(self.add(a, b), c) != self.add(a, self.add(b, c)): raise ValueError("adição não associativa")
            if self.multiply(self.multiply(a, b), c) != self.multiply(a, self.multiply(b, c)): raise ValueError("multiplicação não associativa")
            if self.multiply(a, self.add(b, c)) != self.add(self.multiply(a, b), self.multiply(a, c)): raise ValueError("distributividade esquerda falhou")
            if self.multiply(self.add(a, b), c) != self.add(self.multiply(a, c), self.multiply(b, c)): raise ValueError("distributividade direita falhou")

    def add(self, left: T, right: T) -> T:
        try: return self.addition[left, right]
        except KeyError as exc: raise ValueError("elemento fora do anel") from exc

    def multiply(self, left: T, right: T) -> T:
        try: return self.multiplication[left, right]
        except KeyError as exc: raise ValueError("elemento fora do anel") from exc

    def additive_inverse(self, value: T) -> T:
        for candidate in self.elements:
            if self.add(value, candidate) == self.zero: return candidate
        raise ValueError("elemento fora do anel")

    def units(self) -> tuple[T, ...]:
        return tuple(a for a in self.elements if any(self.multiply(a, b) == self.one and self.multiply(b, a) == self.one for b in self.elements))


def integers_modulo(modulus: int) -> FiniteRing[int]:
    if not 1 <= modulus <= 256: raise ValueError("módulo fora do limite exaustivo")
    elements = tuple(range(modulus))
    return FiniteRing(elements, 0, 1 % modulus,
                      {(a, b): (a + b) % modulus for a in elements for b in elements},
                      {(a, b): (a * b) % modulus for a in elements for b in elements})


__all__ = ["FiniteRing", "integers_modulo"]
