"""Exact symbolic differentiation for the restricted rational expression AST."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from ..expression import Binary, Expr, Number, Symbol


ZERO = Number(Fraction(0))
ONE = Number(Fraction(1))


def _mul(a: Expr, b: Expr) -> Expr:
    if isinstance(a, Number) and a.value == 0:
        return ZERO
    if isinstance(b, Number) and b.value == 0:
        return ZERO
    if isinstance(a, Number) and a.value == 1:
        return b
    if isinstance(b, Number) and b.value == 1:
        return a
    return Binary("*", a, b)


def _add(a: Expr, b: Expr) -> Expr:
    if isinstance(a, Number) and a.value == 0:
        return b
    if isinstance(b, Number) and b.value == 0:
        return a
    return Binary("+", a, b)


def _sub(a: Expr, b: Expr) -> Expr:
    if isinstance(b, Number) and b.value == 0:
        return a
    return Binary("-", a, b)


def _pow(base: Expr, exponent: int) -> Expr:
    if exponent == 0:
        return ONE
    if exponent == 1:
        return base
    return Binary("**", base, Number(Fraction(exponent)))


@dataclass(frozen=True)
class DerivativeResult:
    expression: Expr
    derivative: Expr
    variable: str
    required_nonzero: tuple[Expr, ...] = ()

    def __post_init__(self) -> None:
        Symbol(self.variable)


def _dedupe(expressions: Iterable[Expr]) -> tuple[Expr, ...]:
    return tuple(dict.fromkeys(expressions))


def differentiate(expr: Expr, variable: str) -> DerivativeResult:
    """Differentiate exactly inside the supported arithmetic/power language.

    The returned side conditions are the nonzero expressions required by quotient
    and negative-power rules. They preserve the domain of the original partial
    expression rather than silently extending it.
    """
    Symbol(variable)

    def visit(node: Expr) -> tuple[Expr, tuple[Expr, ...]]:
        if isinstance(node, Number):
            return ZERO, ()
        if isinstance(node, Symbol):
            return (ONE if node.name == variable else ZERO), ()

        da, ca = visit(node.left)
        db, cb = visit(node.right)
        conditions = list(ca + cb)

        if node.op == "+":
            return _add(da, db), _dedupe(conditions)
        if node.op == "-":
            return _sub(da, db), _dedupe(conditions)
        if node.op == "*":
            return _add(_mul(da, node.right), _mul(node.left, db)), _dedupe(conditions)
        if node.op == "/":
            conditions.append(node.right)
            numerator = _sub(_mul(da, node.right), _mul(node.left, db))
            denominator = _pow(node.right, 2)
            return Binary("/", numerator, denominator), _dedupe(conditions)
        if node.op == "**":
            if not isinstance(node.right, Number) or node.right.value.denominator != 1:
                raise ValueError("Derivação suporta apenas expoente inteiro literal")
            exponent = node.right.value.numerator
            if exponent < 0:
                conditions.append(node.left)
            if exponent == 0:
                return ZERO, _dedupe(conditions)
            coefficient = Number(Fraction(exponent))
            return _mul(_mul(coefficient, _pow(node.left, exponent - 1)), da), _dedupe(conditions)
        raise ValueError(f"Operador não suportado para derivação: {node.op}")

    derivative, conditions = visit(expr)
    return DerivativeResult(expr, derivative, variable, conditions)


def symbolic_gradient(expr: Expr, variables: Iterable[str]) -> tuple[DerivativeResult, ...]:
    names = tuple(variables)
    if not names:
        raise ValueError("Gradiente exige ao menos uma variável")
    if len(set(names)) != len(names):
        raise ValueError("Variáveis do gradiente devem ser únicas")
    return tuple(differentiate(expr, name) for name in names)


def symbolic_hessian(expr: Expr, variables: Iterable[str]) -> tuple[tuple[DerivativeResult, ...], ...]:
    first = symbolic_gradient(expr, variables)
    names = tuple(result.variable for result in first)
    rows = []
    for first_result in first:
        row = []
        for name in names:
            second = differentiate(first_result.derivative, name)
            row.append(DerivativeResult(
                expr, second.derivative, name,
                _dedupe(first_result.required_nonzero + second.required_nonzero),
            ))
        rows.append(tuple(row))
    return tuple(rows)


__all__ = ["DerivativeResult", "differentiate", "symbolic_gradient", "symbolic_hessian"]
