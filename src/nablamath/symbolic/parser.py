"""Parser público do subconjunto racional sem avaliação de código."""

from ..expression import Expr, parse_expr


def parse(source: str) -> Expr:
    return parse_expr(source)
