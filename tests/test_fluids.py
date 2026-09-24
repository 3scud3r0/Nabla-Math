import unittest

from nablamath.physics.fluids import PipeFlow
from nablamath.physics.fluids.validation import integrate_profile_midpoint


class FluidsTests(unittest.TestCase):
    def test_profile_and_independent_quadrature(self):
        pipe = PipeFlow(radius_m=.01, length_m=2, pressure_drop_pa=5,
                        dynamic_viscosity_pa_s=1, density_kg_m3=1000)
        result = pipe.solve()
        self.assertAlmostEqual(result.center_velocity_m_s, 2*result.mean_velocity_m_s)
        self.assertAlmostEqual(pipe.velocity_at(pipe.radius_m), 0)
        self.assertAlmostEqual(integrate_profile_midpoint(pipe, 2000),
                               result.volumetric_flow_m3_s,
                               delta=result.volumetric_flow_m3_s*1e-6)
        self.assertTrue(result.laminar_regime_compatible)

    def test_reject_invalid_parameters_and_indicate_out_of_regime(self):
        with self.assertRaises(ValueError):
            PipeFlow(0, 1, 1, 1, 1)
        high = PipeFlow(.1, 1, 10000, .001, 1000).solve()
        self.assertFalse(high.laminar_regime_compatible)
