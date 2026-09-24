"""Revisão explícita da tradução informal para enunciado formal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TranslationReview:
    source_statement: str
    formal_statement: str
    reviewer: str
    accepted: bool
    notes: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.source_statement, self.formal_statement,
                                                self.reviewer, self.notes)):
            raise ValueError("Revisão requer fonte, formalização, revisor e notas")


__all__ = ["TranslationReview"]
