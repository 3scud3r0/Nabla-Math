"""Checagem independente por integração de perfil radial em anéis."""

from math import pi

from .model import PipeFlow


def integrate_profile_midpoint(flow: PipeFlow, rings: int = 1024) -> float:
    if not 1 <= rings <= 1_000_000:
        raise ValueError("Número de anéis fora do intervalo")
    dr = flow.radius_m/rings
    return sum(flow.velocity_at((i+0.5)*dr) * 2*pi*(i+0.5)*dr*dr
               for i in range(rings))
