import unittest
from fractions import Fraction

from nablamath.entity import ExpressionEntity
from nablamath.expression import parse_expr


class ExpressionEntityTests(unittest.TestCase):
    def test_semantic_identity_ignores_source_whitespace(self):
        a = ExpressionEntity.parse("x + y")
        b = ExpressionEntity.parse("(x+y)")
        self.assertEqual(a.expression, b.expression)
        self.assertEqual(a.content_id, b.content_id)

    def test_assumptions_are_part_of_identity(self):
        plain = ExpressionEntity.parse("x/x")
        constrained = ExpressionEntity.parse("x/x", nonzero=("x",))
        self.assertNotEqual(plain.content_id, constrained.content_id)
        optimized = constrained.optimize(operation_costs={"/": 10, "number": 0, "symbol": 0})
        self.assertEqual(str(optimized.expression.value), "1")

    def test_representations_share_one_semantic_source(self):
        entity = ExpressionEntity.parse("(x+x)/3")
        values = {"x": Fraction(5, 2)}
        exact = entity.evaluate(values)
        compiled = entity.compile(backend="python")(values)
        self.assertEqual(exact, compiled)
        descriptor = entity.descriptor()
        self.assertEqual(descriptor["content_id"], entity.content_id)
        self.assertIn("\\frac", entity.latex())

    def test_formal_statement_preserves_entity_assumptions(self):
        entity = ExpressionEntity.parse("x/x", nonzero=("x",))
        source = entity.equivalence_theorem(parse_expr("1"), theorem_name="entity_div_self")
        self.assertIn("(h0 : nabla_x ≠ 0)", source)
        self.assertNotIn("sorry", source)


if __name__ == "__main__":
    unittest.main()