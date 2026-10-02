from dataclasses import replace
from fractions import Fraction
import unittest

from nablamath.expression import DomainError, Symbol, evaluate, parse_expr, render
from nablamath.symbolic import AssumptionSet, RewriteRule, parse_pattern, saturate, verify_saturation_certificate

class DeclarativeEGraphTests(unittest.TestCase):
    def test_custom_rule_does_not_require_saturator_changes(self):
        rule = RewriteRule("double", parse_pattern("?a + ?a"), parse_pattern("2 * ?a"),
                           justification="Definição algébrica de duplicação.", lean_theorem="NablaMath.add_self")
        result = saturate(parse_expr("x+x"), rules=(rule,),
                          operation_costs={"+": 10, "*": 1, "number": 0, "symbol": 0})
        self.assertEqual(render(result.expression), "(2 * x)")
        self.assertTrue(result.certificate_verified)

    def test_divide_self_requires_nonzero_fact(self):
        expression = parse_expr("x/x")
        without = saturate(expression, operation_costs={"/": 10, "number": 0, "symbol": 0})
        self.assertEqual(render(without.expression), "(x / x)")
        with_fact = saturate(expression, assumptions=AssumptionSet.from_nonzero("x"),
                             operation_costs={"/": 10, "number": 0, "symbol": 0})
        self.assertEqual(render(with_fact.expression), "1")
        self.assertTrue(any(step.rule == "divide_self" and step.assumptions == ("x != 0",) for step in with_fact.proof))

    def test_certificate_is_replayable_and_tampering_is_rejected(self):
        result = saturate(parse_expr("x+0"))
        self.assertTrue(result.certificate_verified)
        self.assertTrue(result.proof[0].rule_hash)
        corrupted = replace(result.proof[0], after=Symbol("z"))
        verification = verify_saturation_certificate(result.original, result.expression, (corrupted,), ())
        self.assertFalse(verification.valid)

    def test_partial_domain_is_preserved(self):
        result = saturate(parse_expr("0 * (1/x)"))
        with self.assertRaises(DomainError):
            evaluate(result.expression, {"x": Fraction(0)})

if __name__ == "__main__":
    unittest.main()
