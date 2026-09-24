"""Métricas agregadas, sem expor identidades individuais."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    participants_unique: int
    tasks_created: int
    tasks_verified: int
    window: str


def summarize(events: list[dict], window: str = "all") -> Metrics:
    participants = {event.get("payload", {}).get("participant") for event in events
                    if event.get("payload", {}).get("participant")}
    return Metrics(len(participants), sum(e.get("kind") == "task.created" for e in events),
                   sum(e.get("kind") == "task.verified" for e in events), window)
