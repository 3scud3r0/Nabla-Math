from .base import AgentProposal, contextual_proposal
from ..core.planner import Task


class Researcher:
    name = "researcher"
    kinds = frozenset({"research"})

    def propose(self, task: Task, context: tuple[AgentProposal, ...]) -> AgentProposal:
        return contextual_proposal(self.name, task, context, prefix="Mapear fontes e alternativas",
                                   risks=("fontes ainda não verificadas", "licenças pendentes"))


__all__ = ["Researcher"]
