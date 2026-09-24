"""Estado escalar mínimo para órbita ideal em um referencial inercial."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class OrbitalState:
    radius_m: float
    radial_velocity_m_s: float
    tangential_velocity_m_s: float
    epoch_s: float = 0.0
    frame: str = "two_body_inertial"

    def __post_init__(self) -> None:
        for value in (self.radius_m, self.radial_velocity_m_s,
                      self.tangential_velocity_m_s, self.epoch_s):
            if not isfinite(value):
                raise ValueError("Estado orbital deve ser finito")
        if self.radius_m <= 0 or self.tangential_velocity_m_s < 0:
            raise ValueError("Raio positivo e velocidade tangencial não negativa são necessários")


__all__ = ["OrbitalState"]
