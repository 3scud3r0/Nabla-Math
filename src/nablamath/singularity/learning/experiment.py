"""Reproducible declarative experiments and immutable observations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping


@dataclass(frozen=True)
class Experiment:
    hypothesis_id: str
    method: str
    inputs: Mapping[str, object]
    expected_metrics: tuple[str, ...]
    seed: int = 0

    @property
    def content_id(self) -> str:
        payload = {"hypothesis_id": self.hypothesis_id, "method": self.method,
                   "inputs": self.inputs, "expected_metrics": self.expected_metrics, "seed": self.seed}
        return hashlib.sha256(json.dumps(payload, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Observation:
    experiment_id: str
    metrics: Mapping[str, float]
    artifact_ids: tuple[str, ...] = ()


def validate_observation(experiment: Experiment, observation: Observation) -> None:
    if observation.experiment_id != experiment.content_id:
        raise ValueError("Observação pertence a outro experimento")
    if set(observation.metrics) != set(experiment.expected_metrics):
        raise ValueError("Métricas observadas não correspondem ao protocolo")


__all__ = ["Experiment", "Observation", "validate_observation"]
