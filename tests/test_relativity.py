import unittest

from nablamath.physics.relativity import (
    C_M_S, FourPosition, SchwarzschildMetric, compose_collinear_velocities,
    four_momentum, lorentz_boost_x, lorentz_gamma, mass_shell_relative_error,
    minkowski_christoffel_cartesian, minkowski_interval_squared,
)


class SpecialRelativityTests(unittest.TestCase):
    def test_lorentz_boost_preserves_minkowski_interval(self):
        event = FourPosition(2.0, 1.2e8, -3.0e7, 4.0e7)
        boosted = lorentz_boost_x(event, 0.6 * C_M_S)
        before = minkowski_interval_squared(event)
        after = minkowski_interval_squared(boosted)
        self.assertAlmostEqual(after / before, 1.0, places=13)

    def test_low_velocity_limit_and_velocity_composition(self):
        beta = 1e-4
        gamma = lorentz_gamma(beta * C_M_S)
        self.assertAlmostEqual(gamma, 1.0 + 0.5 * beta * beta, places=15)
        composed = compose_collinear_velocities(0.8 * C_M_S, 0.7 * C_M_S)
        self.assertLess(abs(composed), C_M_S)

    def test_energy_momentum_mass_shell(self):
        momentum = four_momentum(2.0, 0.5 * C_M_S, 0.2 * C_M_S, 0.0)
        self.assertLess(mass_shell_relative_error(momentum), 5e-15)


class GeneralRelativityReferenceTests(unittest.TestCase):
    def test_schwarzschild_geometry_has_expected_limits_and_scaling(self):
        metric = SchwarzschildMetric(5.9722e24)
        rs = metric.schwarzschild_radius_m
        self.assertGreater(rs, 0.0)
        near = metric.static_clock_rate(10 * rs)
        far = metric.static_clock_rate(100 * rs)
        self.assertLess(near, far)
        self.assertLess(far, 1.0)
        k1 = metric.kretschmann_m4_inverse(20 * rs)
        k2 = metric.kretschmann_m4_inverse(40 * rs)
        self.assertAlmostEqual(k1 / k2, 64.0, places=12)

    def test_circular_frequency_and_weak_field_precession_are_positive(self):
        metric = SchwarzschildMetric(1.98847e30)
        self.assertGreater(metric.circular_orbit_angular_velocity_rad_s(1.5e11), 0.0)
        self.assertGreater(metric.weak_field_periapsis_advance_rad_per_orbit(5.79e10, 0.2056), 0.0)

    def test_cartesian_minkowski_christoffels_are_zero(self):
        connection = minkowski_christoffel_cartesian()
        self.assertEqual(len(connection), 4)
        self.assertTrue(all(value == 0.0 for plane in connection for row in plane for value in row))


if __name__ == "__main__":
    unittest.main()
