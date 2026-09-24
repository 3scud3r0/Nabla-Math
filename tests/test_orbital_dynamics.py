import math
import unittest

from nablamath.physics.orbital.dynamics import propagate_radial
from nablamath.physics.orbital.state import OrbitalState


class OrbitalDynamicsTests(unittest.TestCase):
    def test_circular_orbit_preserves_state_over_one_period(self):
        mu, radius = 3.986004418e14, 7_000_000.0
        speed = math.sqrt(mu/radius)
        period = 2*math.pi*radius/speed
        result = propagate_radial(mu, OrbitalState(radius, 0, speed), period, 200)
        self.assertAlmostEqual(result.state.radius_m/radius, 1, places=10)
        self.assertAlmostEqual(result.state.radial_velocity_m_s, 0, places=8)
        self.assertLess(result.energy_error_j_kg, 1e-5)

    def test_eccentric_orbit_changes_tangential_speed_and_returns(self):
        mu, r0 = 3.986004418e14, 7_000_000.0
        a = 9_000_000.0
        v0 = math.sqrt(mu*(2/r0 - 1/a))
        period = 2*math.pi*math.sqrt(a**3/mu)
        start = OrbitalState(r0, 0, v0)
        quarter = propagate_radial(mu, start, period/4, 500)
        self.assertGreater(quarter.state.radius_m, r0)
        self.assertLess(quarter.state.tangential_velocity_m_s, v0)
        self.assertAlmostEqual(quarter.state.radius_m*quarter.state.tangential_velocity_m_s,
                               r0*v0, delta=1e-5)
        full = propagate_radial(mu, start, period, 2000)
        self.assertAlmostEqual(full.state.radius_m/r0, 1, places=7)
        self.assertLess(full.energy_error_j_kg, 0.1)

    def test_rejects_invalid_parameters(self):
        initial = OrbitalState(10, 0, 1)
        for mu, duration, steps in ((0, 1, 10), (1, math.nan, 10), (1, 1, 0)):
            with self.assertRaises(ValueError):
                propagate_radial(mu, initial, duration, steps)
