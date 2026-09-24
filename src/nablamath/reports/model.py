"""Modelo de relatório que conserva conteúdo calculado e proveniência."""

from __future__ import annotations

from dataclasses import dataclass

from ..research import ResearchResult


@dataclass(frozen=True)
class Report:
    title: str
    result: ResearchResult
    references: tuple[str, ...] = ()

    def manifest(self) -> dict:
        return {"title": self.title, "content_id": self.result.content_id,
                "references": list(self.references), "steps": len(self.result.steps),
                "evidence": "exact_instance"}


def build(result: ResearchResult, title: str = "NablaMath research record",
          references: tuple[str, ...] = ()) -> Report:
    if not title.strip():
        raise ValueError("O título não pode ser vazio")
    return Report(title, result, references)


__all__ = ["Report", "build"]
