"""Offline demonstrator for the bounded research orchestrator."""

from __future__ import annotations

import argparse
import json

from ..core.planner import Task
from .api import ResearchAPI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nabla-lab")
    parser.add_argument("objective")
    args = parser.parse_args(argv)
    tasks = (
        Task("research", "research", args.objective, priority=3),
        Task("mathematics", "mathematics", args.objective, ("research",), 2),
        Task("critique", "critique", args.objective, ("mathematics",), 1),
        Task("evaluate", "evaluate", args.objective, ("critique",), 0),
    )
    outcome = ResearchAPI().run(tasks)
    print(json.dumps(outcome.to_data(), ensure_ascii=False, indent=2))
    return 0 if outcome.completed else 1


__all__ = ["main"]
