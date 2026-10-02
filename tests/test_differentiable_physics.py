import math
import unittest

from nablamath.autodiff import Var
from nablamath.physics.differentiable import (
    orbital_terminal_sensitivity, propagate_radial_differentiable, rk4_integrate,
    vertical_reentry_differentiable,
)
from nablamath.physics.orbital import OrbitalState, propagate_radial


class DifferentiablePhysicsTests(unittest.TestCase):
    def test_rk4_preserves_gradient_for_exponential_decay(self):
        y0 = Var(2.0)
        final, = rk4_integrate(lambda _t, y: (-y[0],), (y0,), 0.0, 1.0, 100)
        self.assertIsInstance(final, Var)
        final.backward()
        expected = 2.0 * math.exp(-1.0)
        self.assertAlmostEqual(final.value, expected, places=7)
        self.assertAlmostEqual(y0.grad, math.exp(-1.0), places=7)

    def test_differentiable_orbit_matches_reference_rk4(self):
        mu = 3.986004418e14
        initial = OrbitalState(7_000_000.0, 10.0, 7_500.0)
        reference = propagate_radial(mu, initial, 20.0, steps=40)
        radius, radial, tangential = propagate_radial_differentiable(
            mu, initial.radius_m, initial.radial_velocity_m_s, initial.tangential_velocity_m_s, 20.0, steps=40
        )
        self.assertAlmostEqual(float(radius), reference.state.radius_m, places=6)
        self.assertAlmostEqual(float(radial), reference.state.radial_velocity_m_s, places=8)
        self.assertAlmostEqual(float(tangential), reference.state.tangential_velocity_m_s, places=8)

    def test_orbital_sensitivity_is_finite(self):
        result = orbital_terminal_sensitivity(3.986004418e14, 7_000_000.0, 0.0, 7_500.0, 10.0, steps=20)
        for value in (result.d_final_radius_d_mu, result.d_final_radius_d_radius0,
                      result.d_final_radius_d_radial_velocity0, result.d_final_radius_d_tangential_velocity0):
            self.assertTrue(math.isfinite(value))

    def test_reentry_is_differentiable_wrt_ballistic_coefficient(self):
        beta = Var(250.0)
        result = vertical_reentry_differentiable(80_000.0, 2_000.0, beta, 2.0, steps=20, heat_coefficient=1e-8)
        self.assertIsInstance(result.downward_speed_m_s, Var)
        result.downward_speed_m_s.backward()
        self.assertGreater(beta.grad, 0.0)
        self.assertGreater(result.heat_load_proxy.value, 0.0)


if __name__ == "__main__":
    unittest.main()