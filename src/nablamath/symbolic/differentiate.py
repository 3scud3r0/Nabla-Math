"""Exact symbolic differentiation for the complete rational-expression AST."""

"""Exact symbolic differentiation for the restricted rational expression AST."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from ..expression import Binary, Expr, Number, Symbol


ZERO = Number(Fraction(0))
ONE = Number(Fraction(1))


@dataclass(frozen=True)
class DerivativeStep:
    rule: str
    source: Expr
    result: Expr
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
    variable: str
    expression: Expr
    derivative: Expr
    steps: tuple[DerivativeStep, ...]
    required_nonzero: tuple[Expr, ...]


def _number(value: int | Fraction) -> Number:
    return Number(Fraction(value))


def _simplify(expr: Expr) -> Expr:
    if not isinstance(expr, Binary):
        return expr
    left, right = _simplify(expr.left), _simplify(expr.right)
    if isinstance(left, Number) and isinstance(right, Number):
        if expr.op == "+":
            return Number(left.value + right.value)
        if expr.op == "-":
            return Number(left.value - right.value)
        if expr.op == "*":
            return Number(left.value * right.value)
        if expr.op == "/" and right.value:
            return Number(left.value / right.value)
        if expr.op == "**" and right.value.denominator == 1 and not (
            left.value == 0 and right.value <= 0
        ):
            return Number(left.value ** right.value.numerator)
    if expr.op == "+":
        if left == ZERO:
            return right
        if right == ZERO:
            return left
    if expr.op == "-" and right == ZERO:
        return left
    if expr.op == "*":
        if left == ZERO or right == ZERO:
            return ZERO
        if left == ONE:
            return right
        if right == ONE:
            return left
    if expr.op == "/" and right == ONE:
        return left
    if expr.op == "**" and right == ONE:
        return left
    return Binary(expr.op, left, right)


def differentiate(expr: Expr, variable: str) -> DerivativeResult:
    """Differentiate numbers, symbols, arithmetic and literal integer powers."""
    if not variable.isidentifier():
        raise ValueError("Variável inválida")
    steps: list[DerivativeStep] = []
    constraints: list[Expr] = []

    def collect_domain(node: Expr) -> None:
        if not isinstance(node, Binary):
            return
        if node.op == "/" and node.right not in constraints:
            constraints.append(node.right)
        if (node.op == "**" and isinstance(node.right, Number)
                and node.right.value < 0 and node.left not in constraints):
            constraints.append(node.left)
        collect_domain(node.left)
        collect_domain(node.right)

    collect_domain(expr)

    def visit(node: Expr) -> Expr:
        if isinstance(node, Number):
            result = ZERO
            steps.append(DerivativeStep("constant", node, result))
            return result
        if isinstance(node, Symbol):
            result = ONE if node.name == variable else ZERO
            steps.append(DerivativeStep("symbol", node, result))
            return result
        left_derivative, right_derivative = visit(node.left), visit(node.right)
        if node.op == "+":
            result = Binary("+", left_derivative, right_derivative)
            rule = "sum"
        elif node.op == "-":
            result = Binary("-", left_derivative, right_derivative)
            rule = "difference"
        elif node.op == "*":
            result = Binary("+", Binary("*", left_derivative, node.right),
                            Binary("*", node.left, right_derivative))
            rule = "product"
        elif node.op == "/":
            numerator = Binary("-", Binary("*", left_derivative, node.right),
                               Binary("*", node.left, right_derivative))
            result = Binary("/", numerator, Binary("**", node.right, _number(2)))
            rule = "quotient"
        elif node.op == "**":
            if not isinstance(node.right, Number) or node.right.value.denominator != 1:
                raise ValueError("Derivação de potência requer expoente inteiro literal")
            exponent = node.right.value.numerator
            result = Binary("*", Binary("*", _number(exponent),
                                         Binary("**", node.left, _number(exponent - 1))),
                            left_derivative)
            rule = "integer_power"
        else:
            raise ValueError(f"Operador sem regra de derivação: {node.op}")
        result = _simplify(result)
        steps.append(DerivativeStep(rule, node, result))
        return result

    derivative = visit(expr)
    return DerivativeResult(variable, expr, derivative, tuple(steps), tuple(constraints))


__all__ = ["DerivativeResult", "DerivativeStep", "differentiate"]
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
