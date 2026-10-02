"""Unified semantic expression entity with multiple derived representations."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Mapping

from .compiler import CompiledExpression, compile_program, jax_available, lower_expr
from .expression import Expr, Symbol, evaluate, parse_expr, to_data, to_latex
from .formal import universal_lean_source
from .symbolic import AssumptionSet, SaturationResult, saturate


CAPABILITIES = frozenset({
    "ast", "exact_evaluation", "latex", "egraph", "compile_python",
    "compile_jax", "formal_statement",
})


@dataclass(frozen=True)
class ExpressionEntity:
    expression: Expr
    assumptions: AssumptionSet = AssumptionSet()
    source: str | None = None

    @classmethod
    def parse(cls, source: str, *, nonzero: tuple[str, ...] = ()) -> "ExpressionEntity":
        return cls(parse_expr(source), AssumptionSet.from_nonzero(*nonzero), source)

    @property
    def content_id(self) -> str:
        payload = {
            "schema_version": 1,
            "kind": "expression",
            "expression": to_data(self.expression),
            "assumptions": list(self.assumptions.statements()),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def capabilities(self) -> dict[str, bool]:
        return {
            "ast": True,
            "exact_evaluation": True,
            "latex": True,
            "egraph": True,
            "compile_python": True,
            "compile_jax": jax_available(),
            "formal_statement": True,
        }

    def evaluate(self, values: Mapping[str, Fraction | int | str]) -> Fraction:
        rational = {name: value if isinstance(value, Fraction) else Fraction(value) for name, value in values.items()}
        return evaluate(self.expression, rational)

    def latex(self) -> str:
        return to_latex(self.expression)

    def optimize(self, **kwargs) -> SaturationResult:
        if "assumptions" in kwargs:
            raise ValueError("As hipóteses pertencem à identidade da entidade e não podem ser substituídas aqui")
        return saturate(self.expression, assumptions=self.assumptions, **kwargs)

    def ir(self):
        return lower_expr(self.expression)

    def compile(self, *, backend: str = "python", jit: bool = True) -> CompiledExpression:
        return compile_program(self.ir(), backend=backend, jit=jit)

    def equivalence_theorem(self, rhs: Expr | "ExpressionEntity", *,
                            theorem_name: str = "nablamath_entity_equivalence") -> str:
        target = rhs.expression if isinstance(rhs, ExpressionEntity) else rhs
        nonzero = tuple(Symbol(name) for name in sorted(self.assumptions.nonzero_symbols))
        return universal_lean_source(self.expression, target, nonzero=nonzero, theorem_name=theorem_name)

    def descriptor(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "kind": "expression",
            "content_id": self.content_id,
            "assumptions": list(self.assumptions.statements()),
            "capabilities": self.capabilities(),
            "representations": {
                "ast": to_data(self.expression),
                "latex": self.latex(),
                "compiler_ir": self.ir().to_data(),
            },
        }


__all__ = ["CAPABILITIES", "ExpressionEntity"]