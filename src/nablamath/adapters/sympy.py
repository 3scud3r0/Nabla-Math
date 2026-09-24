"""Ponte segura para SymPy: constrói a expressão a partir da AST, nunca de texto livre."""

from __future__ import annotations

from fractions import Fraction

from ..expression import Binary, Expr, Number, Symbol


def _module():
    try:
        import sympy
    except ImportError as exc:
        raise RuntimeError("Instale o extra simbólico para usar SymPy") from exc
    return sympy


def to_sympy(expr: Expr):
    s = _module()
    if isinstance(expr, Number):
        return s.Rational(expr.value.numerator, expr.value.denominator)
    if isinstance(expr, Symbol):
        return s.Symbol(expr.name)
    left, right = to_sympy(expr.left), to_sympy(expr.right)
    return {"+": lambda: left + right, "-": lambda: left - right,
            "*": lambda: left * right, "/": lambda: left / right,
            "**": lambda: left ** right}[expr.op]()


def from_sympy(expr) -> Expr:
    s = _module()
    if expr.is_Integer or expr.is_Rational:
        return Number(Fraction(int(expr.p), int(expr.q)))
    if expr.is_Symbol and str(expr).isidentifier():
        return Symbol(str(expr))
    if expr.is_Add and len(expr.args) == 2:
        return Binary("+", from_sympy(expr.args[0]), from_sympy(expr.args[1]))
    if expr.is_Mul and len(expr.args) == 2:
        return Binary("*", from_sympy(expr.args[0]), from_sympy(expr.args[1]))
    if expr.is_Pow and expr.exp.is_Integer:
        return Binary("**", from_sympy(expr.base), Number(Fraction(int(expr.exp))))
    raise ValueError(f"Expressão SymPy fora do subconjunto: {expr!s}")


__all__ = ["to_sympy", "from_sympy"]
