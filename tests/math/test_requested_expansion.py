from fractions import Fraction
import math
import unittest

from nablamath.expression import DomainError, evaluate, parse_expr
from nablamath.math.algebra.extensions import AlgebraicField
from nablamath.math.algebra.groebner import Polynomial
from nablamath.math.geometry.differential import coordinate_form, scalar_form
from nablamath.math.logic.smt_linear import LinearInequality, equality, solve_linear_rational
from nablamath.math.number_theory.elliptic_curves import EllipticCurveFp
from nablamath.math.number_theory.primality import aks_is_prime, miller_rabin
from nablamath.math.probability.continuous import (
    ExponentialDistribution,
    NormalDistribution,
    PoissonDistribution,
)
from nablamath.math.probability.stochastic import brownian_motion, euler_maruyama
from nablamath.math.topology.homology import SimplicialComplex
from nablamath.symbolic.differentiate import differentiate
from nablamath.symbolic.series import rational_limit, taylor_series


class RequestedMathematicsExpansionTests(unittest.TestCase):
    def test_exact_quadratic_and_cubic_extensions(self):
        sqrt2_field = AlgebraicField((-2, 0, 1), "√2")
        sqrt2 = sqrt2_field.alpha
        self.assertEqual(sqrt2 * sqrt2, sqrt2_field.element((2,)))
        self.assertEqual(sqrt2 * sqrt2.inverse(), sqrt2_field.element((1,)))
        complex_field = AlgebraicField((1, 0, 1), "i")
        self.assertEqual(complex_field.alpha**2, complex_field.element((-1,)))
        cubic = AlgebraicField((-2, 0, 0, 1), "∛2")
        self.assertEqual(cubic.alpha**3, cubic.element((2,)))
        with self.assertRaises(ValueError):
            AlgebraicField((-1, 0, 1))  # reducible (x-1)(x+1)

    def test_symbolic_derivative_is_exact_and_keeps_domain(self):
        result = differentiate(parse_expr("(x^3 + 2*x)/x"), "x")
        for value in (Fraction(1), Fraction(2), Fraction(-3)):
            self.assertEqual(evaluate(result.derivative, {"x": value}), 2 * value)
        self.assertEqual(len(result.required_nonzero), 1)
        erased = differentiate(parse_expr("0*(1/x)"), "x")
        self.assertEqual(erased.required_nonzero, (parse_expr("x"),))

    def test_simplicial_homology_and_graph_fundamental_group(self):
        circle = SimplicialComplex(((0, 1), (1, 2), (0, 2)))
        self.assertEqual(circle.betti_numbers(), (1, 1))
        self.assertEqual(circle.fundamental_group_rank_1d(), 1)
        filled_triangle = SimplicialComplex(((0, 1, 2),))
        self.assertEqual(filled_triangle.betti_numbers(), (1, 0, 0))
        self.assertTrue(filled_triangle.verify_boundary_squared_zero())
        with self.assertRaises(ValueError):
            filled_triangle.fundamental_group_rank_1d()

    def test_differential_forms_wedge_and_d_squared(self):
        variables = ("x", "y")
        x, y = Polynomial.generator(variables, "x"), Polynomial.generator(variables, "y")
        dx, dy = coordinate_form(variables, 0), coordinate_form(variables, 1)
        self.assertEqual(dx.wedge(dy).components[0][0], (0, 1))
        left = dx.wedge(dy).components[0][1]
        right = dy.wedge(dx).components[0][1]
        self.assertEqual(left, -right)
        function = scalar_form(x**2 * y + y**3)
        self.assertFalse(function.exterior_derivative().components == ())
        second_derivative = function.exterior_derivative().exterior_derivative()
        self.assertEqual(second_derivative.components, ())
        self.assertEqual(dx.wedge(dy).exterior_derivative().degree, 3)

    def test_modern_primality_and_elliptic_curve_group(self):
        primes = (2, 3, 97, 104729, 2**61 - 1)
        composites = (0, 1, 4, 561, 1105, (2**31 - 1) * 3)
        self.assertTrue(all(miller_rabin(value) for value in primes))
        self.assertFalse(any(miller_rabin(value) for value in composites))
        self.assertTrue(aks_is_prime(31))
        self.assertFalse(aks_is_prime(49))
        self.assertEqual([aks_is_prime(value) for value in range(2, 40)],
                         [miller_rabin(value) for value in range(2, 40)])
        curve = EllipticCurveFp(97, 2, 3)
        point = (3, 6)
        self.assertTrue(curve.contains(point))
        self.assertEqual(curve.add(point, curve.negate(point)), None)
        self.assertEqual(curve.multiply(2, point), curve.add(point, point))
        self.assertTrue(curve.contains(curve.multiply(20, point)))

    def test_continuous_distributions_and_stochastic_paths(self):
        normal = NormalDistribution(2, 3)
        self.assertAlmostEqual(normal.cdf(normal.mean), .5)
        self.assertAlmostEqual(normal.quantile(.5), normal.mean, places=9)
        exponential = ExponentialDistribution(2)
        self.assertAlmostEqual(exponential.cdf(exponential.quantile(.75)), .75)
        poisson = PoissonDistribution(4)
        self.assertAlmostEqual(sum(poisson.pmf(index) for index in range(40)), 1, places=12)
        first, second = brownian_motion(1, 100, seed=7), brownian_motion(1, 100, seed=7)
        self.assertEqual(first, second)
        geometric = euler_maruyama(1, 1, 10, lambda _t, x: x,
                                   lambda _t, _x: 0, seed=1)
        self.assertGreater(geometric.values[-1], 2.5)
        self.assertTrue(all(math.isfinite(value) for value in geometric.values))

    def test_exact_linear_rational_smt(self):
        feasible = (
            LinearInequality({"x": 1, "y": 1}, 4),
            LinearInequality({"x": -1}, -1),
            LinearInequality({"y": -1}, -1),
        )
        self.assertTrue(solve_linear_rational(feasible).satisfiable)
        impossible = (*equality({"x": 1}, 1), LinearInequality({"x": -1}, -2))
        self.assertFalse(solve_linear_rational(impossible).satisfiable)

    def test_exact_taylor_jet_and_rational_limit(self):
        series = taylor_series(parse_expr("x^3 + 2*x"), "x", 1, 3)
        self.assertEqual(series.coefficients, (Fraction(3), Fraction(5), Fraction(3), Fraction(1)))
        self.assertEqual(evaluate(series.polynomial, {"x": Fraction(4)}), 72)
        limit = rational_limit(parse_expr("x^2-1"), parse_expr("x-1"), "x", 1)
        self.assertEqual((limit.status, limit.value), ("finite", Fraction(2)))
        pole = rational_limit(parse_expr("1"), parse_expr("x-1"), "x", 1)
        self.assertEqual(pole.status, "infinite_or_sided")


if __name__ == "__main__":
    unittest.main()
