"""Pré-condições mínimas: denominação não nula e conflito em avaliação."""

from fractions import Fraction
from typing import Mapping

from ..expression import Expr, evaluate, render


def require_nonzero(expressions: tuple[Expr, ...], values: Mapping[str, Fraction]) -> tuple[str, ...]:
    conditions = []
    for expr in expressions:
        if evaluate(expr, values) == 0:
            raise ValueError(f"Condição impossível nesta instância: {render(expr)} != 0")
        conditions.append(f"{render(expr)} != 0")
    return tuple(dict.fromkeys(conditions))
