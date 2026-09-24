"""Diagrama SVG escalado da seção plana de uma órbita kepleriana."""

from __future__ import annotations

from math import sqrt
from pathlib import Path

from .orbits import EARTH_EQUATORIAL_RADIUS_M, Orbit


def write_orbit_svg(orbit: Orbit, destination: Path, central_radius_m: float = 0) -> Path:
    """Representa trajetória e foco em escala linear; plano/orientação arbitrários."""
    if not 0 <= central_radius_m <= orbit.pericenter_m:
        raise ValueError("Raio do corpo central fora do intervalo")
    a = orbit.semimajor_axis_m
    c = (orbit.apocenter_m - orbit.pericenter_m) / 2
    b = sqrt(orbit.pericenter_m * orbit.apocenter_m)
    scale = 460 / (2 * a)
    cx, cy = 280.0, 280.0
    focus_x = cx + c * scale
    body = central_radius_m * scale
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 560" '
           f'role="img" aria-labelledby="title description">\n'
           f'<title id="title">Órbita kepleriana ideal</title>\n'
           f'<desc id="description">Elipse em escala; corpo central em um foco. '
           f'Raio mínimo {orbit.pericenter_m:g} m e máximo {orbit.apocenter_m:g} m. '
           f'Não inclui inclinação, atmosfera nem perturbações.</desc>\n'
           f'<rect width="560" height="560" fill="#0b1325"/>\n'
           f'<ellipse cx="{cx:.6f}" cy="{cy:.6f}" rx="{a*scale:.6f}" '
           f'ry="{b*scale:.6f}" fill="none" stroke="#7dd3fc" stroke-width="2"/>\n'
           f'<circle cx="{focus_x:.6f}" cy="{cy:.6f}" r="{body:.6f}" '
           f'fill="#2663a5" stroke="#a5d8ff" stroke-width="1"/>\n'
           f'<circle cx="{focus_x:.6f}" cy="{cy:.6f}" r="2" fill="white"/>\n'
           f'</svg>\n')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding="utf-8")
    return destination


def write_earth_orbit_svg(orbit: Orbit, destination: Path) -> Path:
    return write_orbit_svg(orbit, destination, EARTH_EQUATORIAL_RADIUS_M)
