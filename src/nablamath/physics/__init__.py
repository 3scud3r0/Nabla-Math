"""Modelos físicos delimitados; cada um declara hipóteses e escopo de validação."""

from .differentiable import (
    OrbitalSensitivity, ReentryResult, orbital_terminal_sensitivity,
    propagate_radial_differentiable, rk4_integrate, vertical_reentry_differentiable,
)

__all__ = [
    "OrbitalSensitivity", "ReentryResult", "orbital_terminal_sensitivity",
    "propagate_radial_differentiable", "rk4_integrate", "vertical_reentry_differentiable",
]
