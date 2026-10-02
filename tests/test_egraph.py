from fractions import Fraction
import json
import unittest

from nablamath.expression import Binary, DomainError, Symbol, evaluate, parse_expr, render
from nablamath.symbolic.egraph import saturate


class EqualitySaturationTests(unittest.TestCase):
    def test_folds_constants_and_removes_neutral_elements(self):
        result = saturate(parse_expr("(2 + 3) * (x + 0)"))
        self.assertEqual(evaluate(result.expression, {"x": Fraction(4)}), 20)
        self.assertLess(result.cost, 7)
        self.assertTrue(any(event.rule == "constant_fold" for event in result.proof))

    def test_extracts_factored_form_with_operation_cost(self):
        result = saturate(
            parse_expr("a*b + a*c"),
            operation_costs={"+": 1, "*": 10, "symbol": 0},
        )
        self.assertEqual(render(result.expression), "(a * (b + c))")
        self.assertTrue(any(event.rule == "factor_common_left" for event in result.proof))
        self.assertEqual(result.to_data()["operation_costs"], {"+": 1.0, "*": 10.0, "symbol": 0.0})

    def test_does_not_erase_partial_domain_with_zero_product(self):
        result = saturate(parse_expr("0 * (1/x)"))
        self.assertIsInstance(result.expression, Binary)
        with self.assertRaises(DomainError):
            evaluate(result.expression, {"x": Fraction(0)})

    def test_is_deterministic_and_bounded(self):
        expression = parse_expr("a+b+c+d")
        first = saturate(expression, iteration_limit=2, node_limit=20)
        second = saturate(expression, iteration_limit=2, node_limit=20)
        self.assertEqual(first.expression, second.expression)
        self.assertEqual(first.proof, second.proof)
        self.assertEqual(first.content_id, second.content_id)
        self.assertEqual(json.loads(json.dumps(first.to_data()))["content_id"], first.content_id)
        self.assertLessEqual(first.node_count, 20)
        self.assertEqual(first.stop_reason, "node_limit")

    def test_rejects_invalid_budgets(self):
        with self.assertRaises(ValueError):
            saturate(Symbol("x"), iteration_limit=0)
        with self.assertRaises(ValueError):
            saturate(parse_expr("x+y"), node_limit=2)

    def test_rejects_costs_that_make_extraction_ill_defined(self):
        for cost in (-1, float("inf"), float("nan")):
            with self.subTest(cost=cost), self.assertRaises(ValueError):
                saturate(Symbol("x"), operation_costs={"symbol": cost})

    def test_reports_natural_saturation(self):
        result = saturate(Symbol("x"))
        self.assertTrue(result.saturated)
        self.assertEqual(result.stop_reason, "saturated")
        self.assertEqual(result.iterations, 1)


if __name__ == "__main__":
    unittest.main()
