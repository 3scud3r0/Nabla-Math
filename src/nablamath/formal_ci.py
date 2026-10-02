"""Lean CI: closed instances plus generated universal rewrite proofs."""

from pathlib import Path

from .formal import search_rule_proof, verify_with_lean
from .research import calculate
from .symbolic.rules import DEFAULT_EGRAPH_RULES


def main() -> None:
    project = Path("lean")
    for expression, values in [("(x+x)/x", {"x": 3}), ("1/3 + y", {"y": "2/3"})]:
        check = verify_with_lean(calculate(expression, values), project)
        if not check.verified:
            raise RuntimeError(f"Falha da verificação Lean: {check.detail}")

    registry = {rule.name: rule for rule in DEFAULT_EGRAPH_RULES}
    for name in ("divide_self", "factor_common_left"):
        result = search_rule_proof(registry[name], project)
        if not result.verified:
            diagnostics = " | ".join(f"{attempt.strategy}: {attempt.detail}" for attempt in result.attempts)
            raise RuntimeError(f"Busca formal falhou para {name}: {diagnostics}")


if __name__ == "__main__":
    main()
