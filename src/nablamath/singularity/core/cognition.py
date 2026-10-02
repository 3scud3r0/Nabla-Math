"""Typed hypotheses, decomposition, and evidence-aware comparison."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping


@dataclass(frozen=True)
class Hypothesis:
    statement: str
    assumptions: tuple[str, ...] = ()
    predictions: tuple[str, ...] = ()
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.statement.strip() or len(self.statement) > 16_384:
            raise ValueError("Enunciado vazio ou grande demais")
        if not math.isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("confidence deve estar em [0,1]")

    @property
    def content_id(self) -> str:
        payload = {"statement": self.statement, "assumptions": self.assumptions,
                   "predictions": self.predictions, "confidence": self.confidence}
        return hashlib.sha256(json.dumps(payload, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class EvidenceScore:
    hypothesis_id: str
    supported: int
    contradicted: int
    unknown: int
    score: float


def decompose_problem(objective: str, dimensions: tuple[str, ...]) -> tuple[str, ...]:
    if not objective.strip():
        raise ValueError("Objetivo vazio")
    clean = tuple(dict.fromkeys(item.strip() for item in dimensions if item.strip()))
    return tuple(f"{dimension}: {objective}" for dimension in clean) or (objective,)


def compare_hypothesis(hypothesis: Hypothesis, observations: Mapping[str, bool | None]) -> EvidenceScore:
    supported = contradicted = unknown = 0
    for prediction in hypothesis.predictions:
        result = observations.get(prediction)
        if result is True:
            supported += 1
        elif result is False:
            contradicted += 1
        else:
            unknown += 1
    known = supported + contradicted
    score = (supported - contradicted) / known if known else 0.0
    return EvidenceScore(hypothesis.content_id, supported, contradicted, unknown, score)


__all__ = ["EvidenceScore", "Hypothesis", "compare_hypothesis", "decompose_problem"]
