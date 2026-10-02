from .base import AgentProposal, contextual_proposal
from ..core.planner import Task


class Coder:
    name = "coder"
    kinds = frozenset({"code"})

    def propose(self, task: Task, context: tuple[AgentProposal, ...]) -> AgentProposal:
        return contextual_proposal(self.name, task, context, prefix="Propor patch sem executá-lo",
                                   risks=("requer revisão", "requer sandbox e testes"))


__all__ = ["Coder"]
