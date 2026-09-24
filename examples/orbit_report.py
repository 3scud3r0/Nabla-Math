"""Exemplo de órbita ideal com SVG e saída JSON, sem uso operacional."""

import json
from pathlib import Path

from nablamath.orbits import earth_circular_orbit
from nablamath.orbit_svg import write_earth_orbit_svg


orbit = earth_circular_orbit(400_000)  # metros acima do raio equatorial WGS 84
print(json.dumps(orbit.summary(), indent=2))
output = write_earth_orbit_svg(orbit, Path("orbit_example.svg"))
print("Figura gerada:", output)
