import math
import unittest
from fractions import Fraction

from nablamath.autodiff import jvp
from nablamath.numeric.linear import solve_exact
from nablamath.numeric.ode import refine_error


class NumericTests(unittest.TestCase):
    def test_linear_known_solution_and_singular(self):
        self.assertEqual(solve_exact([[2, 1], [1, -1]], [5, 1]), (2, 1))
        self.assertEqual(solve_exact([[2, 0], [0, 3]], [1, 1]),
                         (Fraction(1, 2), Fraction(1, 3)))
        with self.assertRaises(ValueError):
            solve_exact([[1, 2], [2, 4]], [3, 6])

    def test_rk4_converges_on_exp(self):
        value, indicator = refine_error(lambda t,y:y, 1, 0, 1, 10)
        self.assertAlmostEqual(value, math.e, delta=1e-6)
        self.assertLess(indicator, 1e-5)

    def test_jvp_matches_analytic_and_finite_difference(self):
        value, derivative = jvp(lambda x:x*x*x+2*x, 3, 1)
        self.assertEqual((value, derivative), (33, 29))
        h = 1e-5
        fd = (((3+h)**3+2*(3+h))-((3-h)**3+2*(3-h)))/(2*h)
        self.assertAlmostEqual(derivative, fd, places=8)
