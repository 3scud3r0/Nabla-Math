from .base import AgentProposal, contextual_proposal
from ..core.planner import Task


class Mathematician:
    name = "mathematician"
    kinds = frozenset({"mathematics"})

    def propose(self, task: Task, context: tuple[AgentProposal, ...]) -> AgentProposal:
        return contextual_proposal(self.name, task, context, prefix="Formalizar hipóteses e obrigações",
                                   risks=("prova Lean ausente até checagem do kernel",))


__all__ = ["Mathematician"]
