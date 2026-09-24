"""Trajetória mínima de tentativas e erros sem gravar prompts ou segredos."""

from dataclasses import dataclass, field

from .budget import Budget
from .protocol import Proposal, execute_proposal


@dataclass
class Trajectory:
    budget: Budget = field(default_factory=Budget)
    attempts: list[dict] = field(default_factory=list)

    def try_proposal(self, proposal: Proposal) -> str | None:
        if len(self.attempts) >= self.budget.max_proposals:
            raise ValueError("Cota de propostas esgotada")
        try:
            result = execute_proposal(proposal, self.budget)
            outcome = {"status": "accepted", "content_id": result.content_id}
        except (ValueError, ArithmeticError, RuntimeError) as exc:
            outcome = {"status": "rejected", "reason": type(exc).__name__}
        self.attempts.append(outcome)
        return outcome.get("content_id")
