"""Bounded research-orchestration laboratory, not a claim of AGI or singularity."""

from .system.configuration import LabConfiguration
from .system.orchestrator import ResearchOrchestrator, ResearchOutcome

__all__ = ["LabConfiguration", "ResearchOrchestrator", "ResearchOutcome"]
