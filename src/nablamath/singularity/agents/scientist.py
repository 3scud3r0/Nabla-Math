from .base import AgentProposal, contextual_proposal
from ..core.planner import Task


class Scientist:
    name = "scientist"
    kinds = frozenset({"science"})

    def propose(self, task: Task, context: tuple[AgentProposal, ...]) -> AgentProposal:
        return contextual_proposal(self.name, task, context, prefix="Definir hipótese falsificável e controles",
                                   risks=("validação externa necessária", "incerteza não estimada"))


__all__ = ["Scientist"]
