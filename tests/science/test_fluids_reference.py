import unittest

from nablamath.physics.fluids import PipeFlow
from nablamath.physics.fluids.validation import integrate_profile_midpoint


class FluidsReferenceTests(unittest.TestCase):
    def test_midpoint_profile_converges_to_hagen_poiseuille(self):
        flow = PipeFlow(.01, 2, 5, 1, 1000)
        analytic = flow.solve().volumetric_flow_m3_s
        self.assertAlmostEqual(integrate_profile_midpoint(flow, 2048), analytic, places=9)


if __name__ == "__main__":
    unittest.main()
