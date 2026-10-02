"""Declarative agent proposals; agents do not execute tools or generated code."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core.planner import Task


@dataclass(frozen=True)
class AgentProposal:
    task_id: str
    agent: str
    claim: str
    artifacts: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    requires_review: bool = True


class Agent(Protocol):
    name: str
    kinds: frozenset[str]

    def propose(self, task: Task, context: tuple[AgentProposal, ...]) -> AgentProposal: ...


def contextual_proposal(name: str, task: Task, context: tuple[AgentProposal, ...],
                        *, prefix: str, risks: tuple[str, ...]) -> AgentProposal:
    dependencies = ", ".join(item.agent for item in context) or "nenhuma proposta anterior"
    return AgentProposal(task.identifier, name, f"{prefix}: {task.objective}; contexto: {dependencies}",
                         risks=risks)


__all__ = ["Agent", "AgentProposal", "contextual_proposal"]
