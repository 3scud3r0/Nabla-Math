"""Algoritmos determinísticos para escalonamento de uma única máquina."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class Job:
    identifier: str
    processing_time: Fraction
    due_date: Fraction = Fraction(0)
    weight: Fraction = Fraction(1)

    def __post_init__(self) -> None:
        if not self.identifier:
            raise ValueError("identificador vazio")
        object.__setattr__(self, "processing_time", Fraction(self.processing_time))
        object.__setattr__(self, "due_date", Fraction(self.due_date))
        object.__setattr__(self, "weight", Fraction(self.weight))
        if self.processing_time <= 0:
            raise ValueError("tempo de processamento deve ser positivo")
        if self.weight <= 0:
            raise ValueError("peso deve ser positivo")


@dataclass(frozen=True)
class ScheduledJob:
    job: Job
    start: Fraction
    completion: Fraction
    lateness: Fraction
    tardiness: Fraction


def _jobs(jobs: Iterable[Job]) -> tuple[Job, ...]:
    result = tuple(jobs)
    if len(result) > 1_000_000:
        raise ValueError("quantidade de tarefas excede o limite")
    identifiers = tuple(job.identifier for job in result)
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("identificadores duplicados")
    return result


def shortest_processing_time(jobs: Iterable[Job]) -> tuple[Job, ...]:
    """Ordena pela regra SPT, ótima para soma de tempos de conclusão."""
    return tuple(sorted(_jobs(jobs), key=lambda job: (job.processing_time, job.identifier)))


def earliest_due_date(jobs: Iterable[Job]) -> tuple[Job, ...]:
    """Ordena pela regra EDD, ótima para lateness máxima em máquina única."""
    return tuple(sorted(_jobs(jobs), key=lambda job: (job.due_date, job.identifier)))


def weighted_shortest_processing_time(jobs: Iterable[Job]) -> tuple[Job, ...]:
    """Aplica a regra de Smith para soma ponderada de conclusões."""
    return tuple(
        sorted(
            _jobs(jobs),
            key=lambda job: (job.processing_time / job.weight, job.identifier),
        )
    )


def build_schedule(jobs: Iterable[Job], start: int | Fraction = 0) -> tuple[ScheduledJob, ...]:
    """Materializa tempos de início, conclusão, atraso e tardiness."""
    current = Fraction(start)
    schedule = []
    for job in _jobs(jobs):
        completion = current + job.processing_time
        lateness = completion - job.due_date
        schedule.append(ScheduledJob(job, current, completion, lateness, max(Fraction(), lateness)))
        current = completion
    return tuple(schedule)


def total_weighted_completion(schedule: Iterable[ScheduledJob]) -> Fraction:
    return sum((item.job.weight * item.completion for item in schedule), Fraction())


def maximum_lateness(schedule: Iterable[ScheduledJob]) -> Fraction:
    values = tuple(item.lateness for item in schedule)
    return max(values, default=Fraction())


__all__ = [
    "Job",
    "ScheduledJob",
    "build_schedule",
    "earliest_due_date",
    "maximum_lateness",
    "shortest_processing_time",
    "total_weighted_completion",
    "weighted_shortest_processing_time",
]
