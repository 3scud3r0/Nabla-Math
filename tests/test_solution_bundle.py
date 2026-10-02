import unittest
from fractions import Fraction

from nablamath.entity import ExpressionEntity
from nablamath.solution import solve_expression


class SolutionBundleTests(unittest.TestCase):
    def test_bundle_cross_checks_exact_compiler_and_egraph(self):
        entity = ExpressionEntity.parse("(x+x)/3")
        bundle = solve_expression(entity, {"x": Fraction(5, 2)})
        self.assertEqual(bundle.exact_value, Fraction(5, 3))
        self.assertTrue(all(item.outcome == "passed" for item in bundle.verifications[:2]))
        self.assertEqual(bundle.verifications[-1].outcome, "not_requested")
        self.assertEqual(bundle.to_data()["content_id"], bundle.content_id)
        self.assertEqual(len(bundle.compiler_ir_id), 64)

    def test_bundle_is_deterministic(self):
        entity = ExpressionEntity.parse("x+0")
        first = solve_expression(entity, {"x": 7})
        second = solve_expression(entity, {"x": 7})
        self.assertEqual(first.to_data(), second.to_data())


if __name__ == "__main__":
    unittest.main()