"""Interface de agentes: proposta declarativa de expressão, submetida ao núcleo."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from .budget import Budget
from ..research import ResearchResult, calculate


@dataclass(frozen=True)
class Proposal:
    expression: str
    values: Mapping[str, Fraction | str | int]
    rationale: str


def execute_proposal(proposal: Proposal, budget: Budget = Budget()) -> ResearchResult:
    if len(proposal.expression) > budget.max_expression_chars or not proposal.rationale.strip():
        raise ValueError("Proposta excede a cota ou não tem justificativa")
    return calculate(proposal.expression, proposal.values)
