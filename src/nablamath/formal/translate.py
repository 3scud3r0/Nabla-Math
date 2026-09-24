"""Tradução AST → Lean sem aceitar texto Lean fornecido por terceiros."""

from fractions import Fraction

from ..expression import Binary, Expr, Number, Symbol
from ..research import ResearchResult


def _rational(value: Fraction) -> str:
    numerator = f"({value.numerator} : ℚ)"
    return numerator if value.denominator == 1 else f"({numerator} / ({value.denominator} : ℚ))"


def _term(expr: Expr, values: dict[str, Fraction]) -> str:
    if isinstance(expr, Number):
        return _rational(expr.value)
    if isinstance(expr, Symbol):
        if expr.name not in values:
            raise ValueError(f"Sem valor para símbolo {expr.name}")
        return _rational(values[expr.name])
    left, right = _term(expr.left, values), _term(expr.right, values)
    if expr.op == "**":
        exponent = expr.right.value.numerator if isinstance(expr.right, Number) else None
        if exponent is None:
            raise ValueError("Expoente Lean precisa ser literal inteiro")
        return f"(({left}) ^ ({abs(exponent)} : ℕ))" + ("⁻¹" if exponent < 0 else "")
    return f"({left} {expr.op} {right})"


def lean_source(result: ResearchResult) -> str:
    values = dict(result.values)
    return ("import Mathlib.Tactic\n\n"
            f"-- Instância racional {result.content_id}; gerada de AST restrita.\n"
            f"example : {_term(result.original, values)} = {_rational(result.value)} := by\n"
            "  norm_num\n")


__all__ = ["lean_source"]
