from fractions import Fraction
import unittest

from nablamath.expression import evaluate, parse_expr, render
from nablamath.symbolic import differentiate, symbolic_gradient, symbolic_hessian


class SymbolicDifferentiationTests(unittest.TestCase):
    def test_polynomial_product_and_power_rules(self):
        result = differentiate(parse_expr("x*x + 3*x + 2"), "x")
        self.assertEqual(evaluate(result.derivative, {"x": Fraction(5)}), 13)
        self.assertEqual(result.required_nonzero, ())

    def test_quotient_preserves_domain_condition(self):
        result = differentiate(parse_expr("1/x"), "x")
        self.assertEqual(evaluate(result.derivative, {"x": Fraction(2)}), Fraction(-1, 4))
        self.assertEqual(tuple(render(item) for item in result.required_nonzero), ("x",))

    def test_negative_power_preserves_nonzero_base(self):
        result = differentiate(parse_expr("x**-2"), "x")
        self.assertEqual(evaluate(result.derivative, {"x": Fraction(2)}), Fraction(-1, 4))
        self.assertEqual(tuple(render(item) for item in result.required_nonzero), ("x",))

    def test_gradient_and_hessian(self):
        expr = parse_expr("x*x + x*y + y*y")
        gradient = symbolic_gradient(expr, ("x", "y"))
        self.assertEqual(
            tuple(evaluate(item.derivative, {"x": Fraction(2), "y": Fraction(3)}) for item in gradient),
            (Fraction(7), Fraction(8)),
        )
        hessian = symbolic_hessian(expr, ("x", "y"))
        values = tuple(
            tuple(evaluate(item.derivative, {"x": Fraction(2), "y": Fraction(3)}) for item in row)
            for row in hessian
        )
        self.assertEqual(values, ((Fraction(2), Fraction(1)), (Fraction(1), Fraction(2))))


if __name__ == "__main__":
    unittest.main()
