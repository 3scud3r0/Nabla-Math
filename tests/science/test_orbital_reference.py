import unittest
from math import isclose

from nablamath.orbits import earth_circular_orbit
from nablamath.physics.orbital.validation import validate_orbit


class OrbitalReferenceTests(unittest.TestCase):
    def test_circular_orbit_has_equal_speeds_and_valid_energy(self):
        orbit = earth_circular_orbit(400_000)
        summary = orbit.summary()
        self.assertTrue(isclose(summary["pericenter_speed_m_s"], summary["apocenter_speed_m_s"], rel_tol=1e-12))
        self.assertTrue(validate_orbit(orbit).passed)


if __name__ == "__main__":
    unittest.main()
