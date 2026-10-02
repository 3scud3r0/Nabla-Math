"""Fail-closed multi-agent proposal pipeline with content-addressed memory."""

from __future__ import annotations

from dataclasses import dataclass

from ..agents import Coder, Critic, Mathematician, Researcher, Scientist
from ..agents.base import Agent, AgentProposal
from ..core.memory import MemoryRecord, ResearchMemory
from ..core.planner import Plan
from .configuration import LabConfiguration


@dataclass(frozen=True)
class ResearchOutcome:
    completed: tuple[str, ...]
    proposals: tuple[AgentProposal, ...]
    record_ids: tuple[str, ...]
    failures: tuple[str, ...]

    def to_data(self) -> dict[str, object]:
        return {"completed": list(self.completed),
                "proposals": [proposal.__dict__ for proposal in self.proposals],
                "record_ids": list(self.record_ids), "failures": list(self.failures)}


class ResearchOrchestrator:
    def __init__(self, configuration: LabConfiguration,
                 agents: tuple[Agent, ...] | None = None) -> None:
        self.configuration = configuration
        self.agents = agents or (Researcher(), Mathematician(), Scientist(), Coder(), Critic())
        self.memory = ResearchMemory(configuration.max_memory_records)

    def run(self, plan: Plan) -> ResearchOutcome:
        completed: set[str] = set()
        proposals: list[AgentProposal] = []
        record_ids: list[str] = []
        record_by_task: dict[str, str] = {}
        failures: list[str] = []
        iterations = 0
        while len(completed) < len(plan.tasks) and iterations < self.configuration.max_iterations:
            iterations += 1
            ready = plan.ready(completed)
            if not ready:
                failures.append("nenhuma tarefa pronta")
                break
            for task in ready:
                relevant = tuple(item for item in proposals
                                 if item.task_id in task.dependencies)
                candidates = [agent for agent in self.agents if task.kind in agent.kinds]
                if task.kind == "evaluate":
                    proposal = AgentProposal(task.identifier, "evaluator",
                                             f"Avaliar {len(relevant)} propostas sem promover alegações automaticamente",
                                             risks=tuple(risk for item in relevant for risk in item.risks))
                elif not candidates:
                    failures.append(f"sem agente para {task.identifier}:{task.kind}")
                    continue
                else:
                    proposal = candidates[0].propose(task, relevant)
                proposals.append(proposal)
                parents = tuple(record_by_task[dependency] for dependency in task.dependencies)
                record_id = self.memory.add(MemoryRecord(
                    "agent_proposal", proposal.__dict__, "proposal", parents
                ))
                record_ids.append(record_id)
                record_by_task[task.identifier] = record_id
                completed.add(task.identifier)
        return ResearchOutcome(tuple(key for key in plan.order if key in completed),
                               tuple(proposals), tuple(record_ids), tuple(failures))


__all__ = ["ResearchOrchestrator", "ResearchOutcome"]
