"""Auditable solution bundles tying one semantic entity to independent checks."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Mapping

from .entity import ExpressionEntity
from .expression import Expr, to_data
from .formal import verify_with_lean
from .research import calculate


@dataclass(frozen=True)
class VerificationRecord:
    method: str
    outcome: str
    detail: str

    def __post_init__(self) -> None:
        if self.outcome not in {"passed", "failed", "not_requested"}:
            raise ValueError("Resultado de verificação inválido")


@dataclass(frozen=True)
class SolutionBundle:
    entity_id: str
    exact_value: Fraction
    optimized_expression: Expr
    assumptions: tuple[str, ...]
    verifications: tuple[VerificationRecord, ...]
    limitations: tuple[str, ...]
    compiler_ir_id: str

    def to_data(self) -> dict[str, object]:
        payload = {
            "schema_version": 1,
            "entity_id": self.entity_id,
            "exact_value": {
                "numerator": self.exact_value.numerator,
                "denominator": self.exact_value.denominator,
            },
            "optimized_expression": to_data(self.optimized_expression),
            "assumptions": list(self.assumptions),
            "verifications": [
                {"method": item.method, "outcome": item.outcome, "detail": item.detail}
                for item in self.verifications
            ],
            "limitations": list(self.limitations),
            "compiler_ir_id": self.compiler_ir_id,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return {**payload, "content_id": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}

    @property
    def content_id(self) -> str:
        return str(self.to_data()["content_id"])

    @property
    def verified(self) -> bool:
        required = [item for item in self.verifications if item.outcome != "not_requested"]
        return bool(required) and all(item.outcome == "passed" for item in required)


def solve_expression(
    entity: ExpressionEntity, values: Mapping[str, Fraction | int | str], *,
    formal_project: Path | None = None, operation_costs: Mapping[str, float] | None = None
) -> SolutionBundle:
    exact = entity.evaluate(values)
    optimized = entity.optimize(operation_costs=operation_costs)
    if not optimized.certificate_verified:
        raise RuntimeError("E-graph retornou resultado sem certificado válido")
    compiler = entity.compile(backend="python")
    compiled_value = compiler({name: value if isinstance(value, Fraction) else Fraction(value)
                               for name, value in values.items()})
    if compiled_value != exact:
        raise ArithmeticError("Backend compilado divergiu da avaliação exata")
    records = [
        VerificationRecord("exact_vs_compiler", "passed", "Python IR reproduziu a aritmética racional exata"),
        VerificationRecord("egraph_certificate", "passed", f"{len(optimized.proof)} passos verificados"),
    ]
    if formal_project is None:
        records.append(VerificationRecord("lean_kernel", "not_requested", "verificação formal não solicitada"))
    else:
        if entity.source is None:
            raise ValueError("Verificação Lean de instância requer a fonte original da entidade")
        result = calculate(entity.source, values)
        check = verify_with_lean(result, formal_project)
        records.append(VerificationRecord("lean_kernel", "passed" if check.verified else "failed", check.detail))
    limitations = (
        "optimized_expression_equivalence_is_checked_against_the_declarative_rational_ruleset",
        "python_compiler_check_is_not_an_independent_hardware_implementation",
        "formal_kernel_check_is_optional_unless_a_lean_project_is_supplied",
    )
    return SolutionBundle(
        entity.content_id, exact, optimized.expression, entity.assumptions.statements(),
        tuple(records), limitations, entity.ir().content_id,
    )


__all__ = ["VerificationRecord", "SolutionBundle", "solve_expression"]