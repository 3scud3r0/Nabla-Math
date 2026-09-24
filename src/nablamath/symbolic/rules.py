"""Regras do núcleo e identificadores estáveis para auditoria."""

from ..expression import Expr
from ..research import _rewrite

EQUAL_TERMS = "soma_de_termos_iguais"
CONDITIONAL_CANCEL = "cancelamento_condicional"


def rewrite_once(expr: Expr) -> tuple[Expr, str, tuple[Expr, ...]] | None:
    return _rewrite(expr)
