"""In-process façade for bounded research plans."""

from __future__ import annotations

from ..core.planner import Plan, Task
from ..system.configuration import LabConfiguration
from ..system.orchestrator import ResearchOrchestrator, ResearchOutcome


class ResearchAPI:
    def __init__(self, configuration: LabConfiguration | None = None) -> None:
        self.orchestrator = ResearchOrchestrator(configuration or LabConfiguration())

    def run(self, tasks: tuple[Task, ...]) -> ResearchOutcome:
        return self.orchestrator.run(Plan(tasks, task_limit=self.orchestrator.configuration.max_tasks))


__all__ = ["ResearchAPI"]
