import math
import unittest

from nablamath.autodiff import Var
from nablamath.physics.fea import TrussElement, solve_planar_truss


class PlanarTrussTests(unittest.TestCase):
    def test_single_horizontal_bar_matches_closed_form(self):
        length=2.0
        area=0.01
        young=200e9
        force=10_000.0
        result=solve_planar_truss(
            [(0.0,0.0),(length,0.0)],
            [TrussElement(0,1,area,young)],
            [(0.0,0.0),(force,0.0)],
            fixed_dofs=(0,1,3),
        )
        expected=force*length/(area*young)
        self.assertAlmostEqual(float(result.displacements_m[1][0]),expected,places=15)
        self.assertAlmostEqual(float(result.element_stress_pa[0]),force/area,places=6)
        self.assertAlmostEqual(float(result.reactions_n[0][0]),-force,places=8)

    def test_symmetric_two_bar_truss_has_symmetric_reactions(self):
        nodes=[(-1.0,0.0),(1.0,0.0),(0.0,1.0)]
        elements=[
            TrussElement(0,2,0.01,70e9),
            TrussElement(1,2,0.01,70e9),
        ]
        result=solve_planar_truss(
            nodes,elements,
            [(0.0,0.0),(0.0,0.0),(0.0,-1000.0)],
            fixed_dofs=(0,1,2,3),
        )
        self.assertAlmostEqual(float(result.displacements_m[2][0]),0.0,places=14)
        self.assertAlmostEqual(float(result.reactions_n[0][1]),500.0,places=8)
        self.assertAlmostEqual(float(result.reactions_n[1][1]),500.0,places=8)
        self.assertAlmostEqual(
            float(result.reactions_n[0][0]+result.reactions_n[1][0]),
            0.0,places=8,
        )

    def test_compliance_is_differentiable_in_material_parameters(self):
        area=Var(0.02)
        young=Var(100e9)
        result=solve_planar_truss(
            [(0.0,0.0),(1.5,0.0)],
            [TrussElement(0,1,area,young)],
            [(0.0,0.0),(5000.0,0.0)],
            fixed_dofs=(0,1,3),
        )
        self.assertIsInstance(result.compliance_j,Var)
        result.compliance_j.backward()
        self.assertTrue(math.isfinite(area.grad))
        self.assertTrue(math.isfinite(young.grad))
        self.assertLess(area.grad,0.0)
        self.assertLess(young.grad,0.0)

    def test_unconstrained_mechanism_is_rejected(self):
        with self.assertRaises(ValueError):
            solve_planar_truss(
                [(0.0,0.0),(1.0,0.0)],
                [TrussElement(0,1,0.01,1e9)],
                [(0.0,0.0),(1.0,0.0)],
                fixed_dofs=(0,),
            )


if __name__=="__main__":
    unittest.main()
