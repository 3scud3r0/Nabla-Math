"""Calibrated capability ledger; absence of evidence never becomes capability."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Capability:
    name: str
    success_rate: float
    trials: int
    limitation: str

    def __post_init__(self) -> None:
        if not self.name or self.trials < 0 or not 0 <= self.success_rate <= 1 or not math.isfinite(self.success_rate):
            raise ValueError("Capacidade inválida")


class SelfModel:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def update(self, name: str, successes: int, trials: int, limitation: str) -> Capability:
        if not 0 <= successes <= trials:
            raise ValueError("Contagens de avaliação inválidas")
        capability = Capability(name, successes / trials if trials else 0.0, trials, limitation)
        self._capabilities[name] = capability
        return capability

    def supports(self, name: str, minimum_rate: float = 0.95, minimum_trials: int = 20) -> bool:
        capability = self._capabilities.get(name)
        return bool(capability and capability.trials >= minimum_trials
                    and capability.success_rate >= minimum_rate)

    def snapshot(self) -> tuple[Capability, ...]:
        return tuple(self._capabilities[key] for key in sorted(self._capabilities))


__all__ = ["Capability", "SelfModel"]
