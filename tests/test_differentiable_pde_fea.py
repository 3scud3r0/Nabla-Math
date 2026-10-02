import math
import unittest

from nablamath.autodiff import Var
from nablamath.physics.fea import bar_end_sensitivity, solve_uniform_axial_bar
from nablamath.physics.fluids.burgers import solve_burgers_periodic


class FiniteElementTests(unittest.TestCase):
    def test_uniform_bar_matches_closed_form(self):
        length, area, young, force = 2.0, 0.01, 200e9, 10_000.0
        result = solve_uniform_axial_bar(length, area, young, force, elements=6)
        expected = force * length / (area * young)
        self.assertAlmostEqual(float(result.end_displacement_m), expected, places=15)
        for stress in result.element_stress_pa:
            self.assertAlmostEqual(float(stress), force / area, places=6)

    def test_bar_gradients_match_closed_form(self):
        length, area, young, force = 3.0, 0.02, 70e9, 8_000.0
        result = bar_end_sensitivity(length, area, young, force, elements=4)
        displacement = force * length / (area * young)
        self.assertAlmostEqual(result.end_displacement_m, displacement, places=15)
        self.assertAlmostEqual(result.d_displacement_d_young, -displacement / young, delta=abs(displacement / young)*1e-10)
        self.assertAlmostEqual(result.d_displacement_d_area, -displacement / area, delta=abs(displacement / area)*1e-10)


class BurgersTests(unittest.TestCase):
    def test_constant_field_is_invariant(self):
        result = solve_burgers_periodic([2.0] * 16, 1.0, 0.01, 0.02, steps=10)
        self.assertTrue(all(abs(float(value) - 2.0) < 1e-12 for value in result.values))

    def test_periodic_mean_is_conserved(self):
        initial = [math.sin(2 * math.pi * i / 32) for i in range(32)]
        result = solve_burgers_periodic(initial, 1.0, 0.005, 0.01, steps=20)
        self.assertAlmostEqual(float(result.mean), sum(initial) / len(initial), places=12)

    def test_viscosity_gradient_reduces_energy(self):
        initial = [math.sin(2 * math.pi * i / 24) for i in range(24)]
        viscosity = Var(0.02)
        result = solve_burgers_periodic(initial, 1.0, 0.002, viscosity, steps=10)
        energy = result.energy()
        self.assertIsInstance(energy, Var)
        energy.backward()
        self.assertLess(viscosity.grad, 0.0)


if __name__ == "__main__":
    unittest.main()