"""Revisão de contribuição: consenso de reexecução e quarentena de divergências."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewDecision:
    task_id: str
    status: str
    independent_workers: int
    note: str


def decide(task_id: str, submissions: list[str]) -> ReviewDecision:
    unique = len(set(submissions))
    if not submissions:
        return ReviewDecision(task_id, "pending", 0, "aguarda verificação")
    if unique == 1 and len(submissions) >= 2:
        return ReviewDecision(task_id, "verified", unique, "duas execuções concordam")
    if unique > 1:
        return ReviewDecision(task_id, "quarantined", unique, "resultados divergentes")
    return ReviewDecision(task_id, "pending", unique, "aguarda segunda execução")
