import math
import unittest

from nablamath.autodiff import Var
from nablamath.physics.plasma import MU0, solve_linear_resistive_alfven


class LinearMHDTests(unittest.TestCase):
    def test_zero_perturbation_is_fixed_point(self):
        result=solve_linear_resistive_alfven(
            [0.0]*16,[0.0]*16,1.0,1e-7,1e-6,0.01,0.1,0.1,steps=4
        )
        self.assertTrue(all(float(x)==0.0 for x in result.velocity_m_s))
        self.assertTrue(all(float(x)==0.0 for x in result.magnetic_perturbation_t))

    def test_alfven_speed_matches_definition(self):
        rho=2e-6
        field=0.02
        result=solve_linear_resistive_alfven(
            [0.0]*8,[0.0]*8,2.0,1e-8,rho,field,0.0,0.0,steps=1
        )
        self.assertAlmostEqual(
            result.alfven_speed_m_s,
            abs(field)/math.sqrt(MU0*rho),
            places=12,
        )

    def test_resistive_energy_sensitivity_is_negative(self):
        n=12
        magnetic=[1e-4*math.sin(2*math.pi*i/n) for i in range(n)]
        eta=Var(0.05)
        result=solve_linear_resistive_alfven(
            [0.0]*n,magnetic,1.0,2e-8,1e-4,0.005,eta,0.01,steps=2
        )
        energy=result.energy_j_per_m2()
        self.assertIsInstance(energy,Var)
        energy.backward()
        self.assertTrue(math.isfinite(eta.grad))
        self.assertLess(eta.grad,0.0)

    def test_stability_guard(self):
        with self.assertRaises(ValueError):
            solve_linear_resistive_alfven(
                [0.0]*4,[0.0]*4,1.0,1.0,1.0,1.0,0.0,0.0,steps=1
            )


if __name__=="__main__":
    unittest.main()
