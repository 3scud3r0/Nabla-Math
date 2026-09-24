import math
import unittest

from nablamath.orbits import Orbit, earth_circular_orbit, EARTH_MU_M3_S2


class OrbitTests(unittest.TestCase):
    def test_circular_leo_and_kepler_law(self):
        orbit = earth_circular_orbit(400_000)
        data = orbit.summary()
        self.assertAlmostEqual(data["pericenter_speed_m_s"], 7668.56, delta=15)
        self.assertAlmostEqual(data["period_s"] / 60, 92.56, delta=0.5)
        self.assertAlmostEqual(data["pericenter_speed_m_s"]**2 * orbit.pericenter_m,
                               EARTH_MU_M3_S2, delta=EARTH_MU_M3_S2 * 1e-12)
        self.assertAlmostEqual(data["eccentricity"], 0)

    def test_elliptical_conserves_energy_and_angular_momentum(self):
        orbit = Orbit(EARTH_MU_M3_S2, 7e6, 14e6)
        p, a = orbit.pericenter_m, orbit.apocenter_m
        vp, va = orbit.speed_m_s(p), orbit.speed_m_s(a)
        self.assertAlmostEqual(p * vp, a * va, delta=p * vp * 1e-12)
        self.assertAlmostEqual(vp**2 / 2 - orbit.mu_m3_s2 / p,
                               va**2 / 2 - orbit.mu_m3_s2 / a, delta=1e-7)
        self.assertGreater(vp, va)

    def test_domain(self):
        for altitude in (-1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                earth_circular_orbit(altitude)
        with self.assertRaises(ValueError):
            Orbit(1, 10, 9)
        with self.assertRaises(ValueError):
            Orbit(1, 10, 20).speed_m_s(21)
