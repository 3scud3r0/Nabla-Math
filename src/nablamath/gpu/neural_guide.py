"""Small auditable INT8 linear policy for ranking symbolic actions."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


@dataclass(frozen=True)
class QuantizedLinearGuide:
    """Symmetric per-tensor INT8 policy with deterministic integer accumulation."""

    actions: tuple[str, ...]
    weights: tuple[tuple[int, ...], ...]
    biases: tuple[int, ...]
    weight_scale: float
    feature_scale: float

    def __post_init__(self) -> None:
        if not self.actions or len(set(self.actions)) != len(self.actions):
            raise ValueError("Ações devem ser únicas e não vazias")
        if len(self.weights) != len(self.actions) or len(self.biases) != len(self.actions):
            raise ValueError("Uma linha de pesos e bias é exigida por ação")
        width = len(self.weights[0]) if self.weights else 0
        if width < 1 or any(len(row) != width for row in self.weights):
            raise ValueError("Matriz de pesos deve ser retangular e não vazia")
        if any(not -127 <= value <= 127 for row in self.weights for value in row):
            raise ValueError("Pesos precisam caber em INT8 simétrico")
        if not all(math.isfinite(scale) and scale > 0
                   for scale in (self.weight_scale, self.feature_scale)):
            raise ValueError("Escalas devem ser finitas e positivas")

    @property
    def feature_count(self) -> int:
        return len(self.weights[0])

    @classmethod
    def quantize(cls, actions: Sequence[str], weights: Sequence[Sequence[float]],
                 biases: Sequence[float] | None = None, *, feature_scale: float = 1 / 127) -> QuantizedLinearGuide:
        rows = [list(map(float, row)) for row in weights]
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("Matriz de pesos inválida")
        maximum = max((abs(value) for row in rows for value in row), default=0.0)
        weight_scale = maximum / 127 if maximum else 1.0
        quantized = tuple(tuple(max(-127, min(127, round(value / weight_scale)))
                                 for value in row) for row in rows)
        raw_biases = list(biases or [0.0] * len(rows))
        accumulator_scale = weight_scale * feature_scale
        quantized_biases = tuple(round(value / accumulator_scale) for value in raw_biases)
        return cls(tuple(actions), quantized, quantized_biases, weight_scale, feature_scale)

    def logits(self, features: Sequence[float]) -> tuple[float, ...]:
        if len(features) != self.feature_count:
            raise ValueError("Número incorreto de features")
        if any(not math.isfinite(float(value)) for value in features):
            raise ValueError("Features devem ser finitas")
        quantized_features = tuple(max(-127, min(127, round(float(value) / self.feature_scale)))
                                   for value in features)
        scale = self.weight_scale * self.feature_scale
        return tuple((sum(weight * feature for weight, feature in zip(row, quantized_features)) + bias)
                     * scale for row, bias in zip(self.weights, self.biases))

    def rank(self, features: Sequence[float]) -> tuple[tuple[str, float], ...]:
        return tuple(sorted(zip(self.actions, self.logits(features)),
                            key=lambda item: (-item[1], item[0])))


__all__ = ["QuantizedLinearGuide"]
