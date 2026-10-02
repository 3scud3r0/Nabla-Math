"""Dependency-plan visualization without browser or graph dependencies."""

from ..core.planner import Plan


def plan_to_dot(plan: Plan) -> str:
    lines = ["digraph research_plan {"]
    for task in plan.tasks:
        label = task.objective.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  "{task.identifier}" [label="{task.kind}: {label}"];')
        lines.extend(f'  "{dependency}" -> "{task.identifier}";'
                     for dependency in task.dependencies)
    lines.append("}")
    return "\n".join(lines) + "\n"


__all__ = ["plan_to_dot"]
