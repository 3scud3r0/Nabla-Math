from .base import AgentProposal
from ..core.planner import Task


class Critic:
    name = "critic"
    kinds = frozenset({"critique", "test"})

    def propose(self, task: Task, context: tuple[AgentProposal, ...]) -> AgentProposal:
        risks = tuple(dict.fromkeys(risk for proposal in context for risk in proposal.risks))
        claim = f"Criticar {task.objective}: {len(context)} propostas, {len(risks)} riscos distintos"
        return AgentProposal(task.identifier, self.name, claim, risks=risks or ("sem evidência suficiente",))


__all__ = ["Critic"]
