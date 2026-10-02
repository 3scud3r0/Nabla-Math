"""Typed assumptions and domain facts for symbolic transformations."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping
from ..expression import Binary, Expr, Number, Symbol, evaluate, render

@dataclass(frozen=True)
class AssumptionSet:
    nonzero_symbols: frozenset[str] = frozenset()

    @classmethod
    def from_nonzero(cls, *symbols: str) -> "AssumptionSet":
        for name in symbols:
            Symbol(name)  # validate through the core identifier contract
        return cls(frozenset(symbols))

    def proves_nonzero(self, expr: Expr) -> bool:
        if isinstance(expr, Number):
            return expr.value != 0
        if isinstance(expr, Symbol):
            return expr.name in self.nonzero_symbols
        if expr.op == "*":
            return self.proves_nonzero(expr.left) and self.proves_nonzero(expr.right)
        if expr.op == "/":
            return self.proves_nonzero(expr.left) and self.proves_nonzero(expr.right)
        if expr.op == "**":
            return self.proves_nonzero(expr.left)
        return False

    def statements(self) -> tuple[str, ...]:
        return tuple(f"{name} != 0" for name in sorted(self.nonzero_symbols))


def require_nonzero(expressions: tuple[Expr, ...], values: Mapping[str, Fraction]) -> tuple[str, ...]:
    conditions = []
    for expr in expressions:
        if evaluate(expr, values) == 0:
            raise ValueError(f"Condição impossível nesta instância: {render(expr)} != 0")
        conditions.append(f"{render(expr)} != 0")
    return tuple(dict.fromkeys(conditions))

__all__ = ["AssumptionSet", "require_nonzero"]
