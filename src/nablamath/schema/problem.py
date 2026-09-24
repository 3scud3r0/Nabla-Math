"""Enunciado estruturado com hipóteses e fontes declaradas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    identifier: str
    question: str
    assumptions: tuple[str, ...] = ()
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.question.strip():
            raise ValueError("Problema requer identificador e pergunta")
        if any(not item.strip() for item in self.assumptions + self.references):
            raise ValueError("Hipóteses e fontes não podem ser vazias")
