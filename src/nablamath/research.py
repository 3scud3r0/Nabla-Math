"""Derivações com regras explícitas, condições de domínio e cálculo exato."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Mapping

from .expression import Binary, Expr, Number, Symbol, evaluate, parse_expr, render, to_data


@dataclass(frozen=True)
class Step:
    rule: str
    before: Expr
    after: Expr
    required_nonzero: tuple[Expr, ...] = ()

    def to_data(self) -> dict:
        return {
            "rule": self.rule,
            "before": to_data(self.before),
            "after": to_data(self.after),
            "required_nonzero": [to_data(x) for x in self.required_nonzero],
            "verification": "structural_rule_and_exact_instance",
        }


@dataclass(frozen=True)
class ResearchResult:
    source: str
    original: Expr
    simplified: Expr
    values: Mapping[str, Fraction]
    value: Fraction
    steps: tuple[Step, ...]
    nonzero: tuple[Expr, ...]
    content_id: str

    def to_data(self) -> dict:
        return {
            "schema_version": 1,
            "content_id": self.content_id,
            "source": self.source,
            "original": to_data(self.original),
            "simplified": to_data(self.simplified),
            "values": {k: str(v) for k, v in sorted(self.values.items())},
            "value": str(self.value),
            "steps": [step.to_data() for step in self.steps],
            "assumptions": [f"{render(expr)} != 0" for expr in self.nonzero],
            "evidence": "exact_rational_evaluation_and_structural_rewrite",
            "formal_proof": None,
        }


def _rewrite(expr: Expr) -> tuple[Expr, str, tuple[Expr, ...]] | None:
    """Uma regra por chamada; nunca apaga a condição de um denominador cancelado."""
    if not isinstance(expr, Binary):
        return None
    if expr.op == "+" and expr.left == expr.right:
        return Binary("*", Number(Fraction(2)), expr.left), "soma_de_termos_iguais", ()
    if expr.op == "/" and isinstance(expr.left, Binary) and expr.left.op == "*":
        product = expr.left
        if product.right == expr.right:
            return product.left, "cancelamento_condicional", (expr.right,)
        if product.left == expr.right:
            return product.right, "cancelamento_condicional", (expr.right,)
    child = _rewrite(expr.left)
    if child is not None:
        after, rule, conditions = child
        return Binary(expr.op, after, expr.right), rule, conditions
    child = _rewrite(expr.right)
    if child is not None:
        after, rule, conditions = child
        return Binary(expr.op, expr.left, after), rule, conditions
    return None


def calculate(source: str, values: Mapping[str, Fraction | int | str]) -> ResearchResult:
    original = parse_expr(source)
    if any(not isinstance(v, (Fraction, int, str)) or isinstance(v, bool) or
           (isinstance(v, str) and len(v) > 256) for v in values.values()):
        raise ValueError("Valores devem ser inteiros ou frações racionais finitas")
    rational_values = {k: Fraction(v) for k, v in values.items()}
    before_value = evaluate(original, rational_values)
    current = original
    steps: list[Step] = []
    nonzero: list[Expr] = []
    for _ in range(64):
        rewritten = _rewrite(current)
        if rewritten is None:
            break
        after, rule, conditions = rewritten
        for condition in conditions:
            if evaluate(condition, rational_values) == 0:
                raise ValueError("Hipótese de cancelamento não satisfeita")
            if condition not in nonzero:
                nonzero.append(condition)
        if evaluate(after, rational_values) != before_value:
            raise ArithmeticError("Uma transformação alterou o resultado exato")
        steps.append(Step(rule, current, after, conditions))
        current = after
    else:
        raise RuntimeError("Limite de passos atingido")
    payload = {
        "schema_version": 1,
        "source": source,
        "original": to_data(original),
        "simplified": to_data(current),
        "values": {k: str(v) for k, v in sorted(rational_values.items())},
        "steps": [step.to_data() for step in steps],
        "nonzero": [to_data(expr) for expr in nonzero],
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    identifier = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ResearchResult(source, original, current, rational_values, before_value,
                          tuple(steps), tuple(nonzero), identifier)
