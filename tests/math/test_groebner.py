from fractions import Fraction
import unittest

from nablamath.expression import parse_expr
from nablamath.math.algebra.groebner import (
    Polynomial,
    divide_polynomial,
    groebner_basis,
    is_in_ideal,
    polynomial_from_expr,
    s_polynomial,
)


class GroebnerTests(unittest.TestCase):
    def setUp(self):
        self.variables = ("x", "y")
        self.x = Polynomial.generator(self.variables, "x")
        self.y = Polynomial.generator(self.variables, "y")

    def test_sparse_arithmetic_is_exact_and_canonical(self):
        polynomial = (self.x + self.y) ** 3
        self.assertEqual(polynomial.evaluate({"x": 1, "y": 2}), 27)
        self.assertEqual(polynomial - polynomial, Polynomial.zero(self.variables))
        self.assertEqual((Fraction(1, 3) * self.x).evaluate({"x": 3, "y": 0}), 1)

    def test_ast_conversion_accepts_polynomial_subset(self):
        polynomial = polynomial_from_expr(parse_expr("(x+y)^2 - 2*x*y"), self.variables)
        self.assertEqual(polynomial, self.x**2 + self.y**2)
        self.assertEqual(polynomial_from_expr(polynomial.to_expr(), self.variables), polynomial)
        with self.assertRaises(ValueError):
            polynomial_from_expr(parse_expr("1/x"), self.variables)

    def test_multivariate_division_reconstructs_dividend(self):
        dividend = self.x**2 * self.y + self.x * self.y**2 + self.y**2
        divisors = (self.x * self.y - 1, self.y**2 - 1)
        quotients, remainder = divide_polynomial(dividend, divisors, order="lex")
        reconstructed = remainder
        for quotient, divisor in zip(quotients, divisors):
            reconstructed += quotient * divisor
        self.assertEqual(reconstructed, dividend)
        for divisor in divisors:
            self.assertFalse(any(
                all(a <= b for a, b in zip(divisor.leading_term("lex")[0], monomial))
                for monomial, _ in remainder.terms
            ))

    def test_buchberger_basis_reduces_all_s_polynomials(self):
        generators = (self.x * self.y - 1, self.y**2 - self.x)
        basis = groebner_basis(generators, order="lex")
        self.assertTrue(basis)
        for first_index, first in enumerate(basis):
            for second in basis[first_index + 1:]:
                _, remainder = divide_polynomial(s_polynomial(first, second, "lex"),
                                                 basis, order="lex")
                self.assertTrue(remainder.is_zero)
        for generator in generators:
            self.assertTrue(is_in_ideal(generator, basis, order="lex"))
        combination = generators[0] * self.x + generators[1] * self.y
        self.assertTrue(is_in_ideal(combination, basis, order="lex"))

    def test_invalid_rings_and_budgets_fail_closed(self):
        z = Polynomial.generator(("z",), "z")
        with self.assertRaises(ValueError):
            _ = self.x + z
        with self.assertRaises(ZeroDivisionError):
            divide_polynomial(self.x, (Polynomial.zero(self.variables),))
        with self.assertRaises(RuntimeError):
            groebner_basis((self.x * self.y - 1, self.y**2 - self.x), pair_limit=1)


if __name__ == "__main__":
    unittest.main()
