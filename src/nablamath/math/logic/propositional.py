"""Lógica proposicional finita, sem parser ou provador automático."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping, Protocol


class Proposition(Protocol):
    def evaluate(self, values: Mapping[str, bool]) -> bool: ...
    def variables(self) -> frozenset[str]: ...


@dataclass(frozen=True)
class Var:
    name: str
    def __post_init__(self) -> None:
        if not self.name: raise ValueError("variável vazia")
    def evaluate(self, values: Mapping[str, bool]) -> bool:
        if self.name not in values: raise ValueError(f"valor ausente: {self.name}")
        value = values[self.name]
        if not isinstance(value, bool): raise ValueError("valoração deve ser booleana")
        return value
    def variables(self) -> frozenset[str]: return frozenset({self.name})

@dataclass(frozen=True)
class Not:
    value: Proposition
    def evaluate(self, values: Mapping[str, bool]) -> bool: return not self.value.evaluate(values)
    def variables(self) -> frozenset[str]: return self.value.variables()

@dataclass(frozen=True)
class Binary:
    left: Proposition
    right: Proposition
    def variables(self) -> frozenset[str]: return self.left.variables() | self.right.variables()

@dataclass(frozen=True)
class And(Binary):
    def evaluate(self, values: Mapping[str, bool]) -> bool: return self.left.evaluate(values) and self.right.evaluate(values)

@dataclass(frozen=True)
class Or(Binary):
    def evaluate(self, values: Mapping[str, bool]) -> bool: return self.left.evaluate(values) or self.right.evaluate(values)

@dataclass(frozen=True)
class Implies(Binary):
    def evaluate(self, values: Mapping[str, bool]) -> bool: return not self.left.evaluate(values) or self.right.evaluate(values)

@dataclass(frozen=True)
class Iff(Binary):
    def evaluate(self, values: Mapping[str, bool]) -> bool: return self.left.evaluate(values) == self.right.evaluate(values)


def truth_table(proposition: Proposition, *, max_variables: int = 16) -> tuple[tuple[dict[str, bool], bool], ...]:
    names = sorted(proposition.variables())
    if len(names) > max_variables: raise ValueError("tabela verdade excede o limite")
    return tuple((dict(zip(names, values, strict=True)), proposition.evaluate(dict(zip(names, values, strict=True))))
                 for values in product((False, True), repeat=len(names)))


def is_tautology(proposition: Proposition) -> bool:
    return all(result for _, result in truth_table(proposition))


def equivalent(left: Proposition, right: Proposition) -> bool:
    return is_tautology(Iff(left, right))


__all__ = ["And", "Iff", "Implies", "Not", "Or", "Proposition", "Var", "equivalent", "is_tautology", "truth_table"]
