from fractions import Fraction
import random
import unittest

from nablamath.expression import parse_expr
from nablamath.math.algebra.f4 import build_macaulay_matrix, f4_basis
from nablamath.math.algebra.f5 import f5_basis
from nablamath.math.algebra.groebner import Polynomial, divide_polynomial, s_polynomial
from nablamath.math.analysis.laurent import rational_laurent_series, rational_residue
from nablamath.math.geometry.riemannian import MetricJet, riemannian_tensors
from nablamath.math.logic.cdcl import solve_cdcl
from nablamath.math.logic.smt_theories import (ArrayValue, BitVector, DifferenceConstraint,
                                               solve_integer_difference_logic,
                                               verify_difference_result)
from nablamath.math.logic.superposition import (Atom, FOLiteral, function,
                                                superposition_refutation, unify, variable,
                                                verify_superposition)
from nablamath.math.logic.sat import solve_sat, verify_assignment, normalize_cnf
from nablamath.math.probability.ito import ito_formula


class AdvancedRequestedAlgorithmsTests(unittest.TestCase):
    def test_f4_builds_macaulay_matrices_and_satisfies_buchberger(self):
        variables = ("x", "y")
        x, y = Polynomial.generator(variables, "x"), Polynomial.generator(variables, "y")
        generators = (x * y - 1, y**2 - x)
        matrix = build_macaulay_matrix((s_polynomial(*generators, order="lex"),),
                                       generators, order="lex")
        self.assertGreaterEqual(len(matrix.rows), matrix.source_rows)
        self.assertTrue(matrix.monomials)
        result = f4_basis(generators, order="lex")
        self.assertGreater(result.matrices, 0)
        self.assertGreater(result.maximum_nonzeros, 0)
        for left_index, left in enumerate(result.basis):
            for right in result.basis[left_index + 1:]:
                _, remainder = divide_polynomial(s_polynomial(left, right, "lex"),
                                                 result.basis, order="lex")
                self.assertTrue(remainder.is_zero)

    def test_f5_signatures_produce_verified_groebner_basis(self):
        variables = ("x", "y")
        x, y = Polynomial.generator(variables, "x"), Polynomial.generator(variables, "y")
        result = f5_basis((x * y - 1, y**2 - x), order="lex")
        self.assertGreater(result.processed_pairs, 0)
        self.assertEqual(len(result.basis), len(result.labeled_basis))
        for left_index, left in enumerate(result.basis):
            for right in result.basis[left_index + 1:]:
                _, remainder = divide_polynomial(s_polynomial(left, right, "lex"),
                                                 result.basis, order="lex")
                self.assertTrue(remainder.is_zero)

    def test_smt_bit_vectors_arrays_and_integer_difference_logic(self):
        maximum = BitVector(8, 255)
        self.assertEqual((maximum + BitVector(8, 2)).value, 1)
        self.assertEqual(maximum.signed, -1)
        self.assertTrue(maximum.signed_less_than(BitVector(8, 0)))
        array = ArrayValue(0).store("x", 7).store("x", 9)
        self.assertEqual(array.select("x"), 9)
        self.assertEqual(array.select("y"), 0)
        feasible = (DifferenceConstraint("x", "y", 3),
                    DifferenceConstraint("y", "x", -2))
        result = solve_integer_difference_logic(feasible)
        self.assertTrue(result.satisfiable)
        self.assertTrue(verify_difference_result(feasible, result))
        impossible = feasible + (DifferenceConstraint("x", "y", 1),)
        result = solve_integer_difference_logic(impossible)
        self.assertFalse(result.satisfiable)
        self.assertTrue(verify_difference_result(impossible, result))

    def test_first_order_superposition_refutes_equality_problem(self):
        a, b = function("a"), function("b")
        equality = FOLiteral(Atom("=", (a, b)))
        positive = FOLiteral(Atom("P", (a,)))
        negative = FOLiteral(Atom("P", (b,)), positive=False)
        proof = superposition_refutation(({equality}, {positive}, {negative}), step_limit=100)
        self.assertTrue(proof.refuted)
        self.assertFalse(proof.steps[-1].clause)
        self.assertTrue(verify_superposition(proof))
        self.assertIn("superposition", {step.rule for step in proof.steps})
        x = variable("x")
        self.assertIsNone(unify(x, function("f", x)))

    def test_cdcl_cross_checks_dpll_on_random_small_cnfs(self):
        generator = random.Random(42)
        for _ in range(100):
            clauses = []
            for _ in range(generator.randint(1, 14)):
                clause = set()
                for _ in range(generator.randint(1, 4)):
                    variable = generator.randint(1, 7)
                    clause.add(variable if generator.random() < .5 else -variable)
                clauses.append(clause)
            expected = solve_sat(clauses)
            actual = solve_cdcl(clauses, restart_interval=5)
            self.assertEqual(actual.satisfiable, expected.satisfiable, clauses)
            if actual.satisfiable:
                self.assertTrue(verify_assignment(normalize_cnf(clauses), dict(actual.assignment)))

    def test_exact_laurent_series_and_residue(self):
        series = rational_laurent_series(parse_expr("1"), parse_expr("x*(x-1)"),
                                         "x", 0, order=3)
        self.assertEqual(series.pole_order, 1)
        self.assertEqual(series.residue, -1)
        self.assertEqual(series.coefficient(0), -1)
        self.assertEqual(rational_residue(parse_expr("x+2"), parse_expr("x-1"),
                                          "x", 1), 3)

    def test_exact_riemann_tensor_for_cartesian_and_polar_plane(self):
        zero2 = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0)))
        zero3 = (zero2, zero2)
        zero4 = (zero3, zero3)
        euclidean = riemannian_tensors(MetricJet(((1, 0), (0, 1)), zero3, zero4))
        self.assertEqual(euclidean.scalar_curvature, 0)
        first = (
            ((0, 0), (0, 4)),
            ((0, 0), (0, 0)),
        )
        second = (
            (((0, 0), (0, 2)), ((0, 0), (0, 0))),
            (((0, 0), (0, 0)), ((0, 0), (0, 0))),
        )
        polar = riemannian_tensors(MetricJet(((1, 0), (0, 4)), first, second))
        self.assertEqual(polar.scalar_curvature, 0)
        self.assertEqual(polar.christoffel[0][1][1], -2)
        self.assertEqual(polar.christoffel[1][0][1], Fraction(1, 2))

    def test_symbolic_ito_formula_for_brownian_square(self):
        variables = ("t", "x")
        x = Polynomial.generator(variables, "x")
        zero = Polynomial.zero(variables)
        one = Polynomial.constant(variables, 1)
        differential = ito_formula(x**2, zero, one)
        self.assertEqual(differential.dt, one)
        self.assertEqual(differential.dW, 2 * x)


if __name__ == "__main__":
    unittest.main()
