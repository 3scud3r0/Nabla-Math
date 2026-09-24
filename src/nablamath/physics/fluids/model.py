"""Solução analítica de Hagen–Poiseuille; não é um solver Navier–Stokes geral."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite, pi


@dataclass(frozen=True)
class PipeFlow:
    """Escoamento estacionário incompressível, laminar, desenvolvido, tubo circular."""

    radius_m: float
    length_m: float
    pressure_drop_pa: float
    dynamic_viscosity_pa_s: float
    density_kg_m3: float

    def __post_init__(self) -> None:
        for value in asdict(self).values():
            if not isfinite(value) or value <= 0:
                raise ValueError("Entradas devem ser finitas e positivas em SI")

    def velocity_at(self, radial_distance_m: float) -> float:
        if not isfinite(radial_distance_m) or not 0 <= radial_distance_m <= self.radius_m:
            raise ValueError("Posição radial fora do tubo")
        return (self.pressure_drop_pa/(4*self.dynamic_viscosity_pa_s*self.length_m)
                *(self.radius_m**2-radial_distance_m**2))

    def solve(self) -> PipeResult:
        mean = self.velocity_at(0)/2
        flow = pi*self.radius_m**2*mean
        reynolds = self.density_kg_m3*mean*(2*self.radius_m)/self.dynamic_viscosity_pa_s
        return PipeResult(flow, mean, self.velocity_at(0), reynolds,
                          reynolds < 2300,
                          ("newtonian_fluid", "incompressible", "fully_developed",
                           "steady", "circular_pipe", "no_slip"))


@dataclass(frozen=True)
class PipeResult:
    volumetric_flow_m3_s: float
    mean_velocity_m_s: float
    center_velocity_m_s: float
    reynolds_number: float
    laminar_regime_compatible: bool
    assumptions: tuple[str, ...]
