import unittest
from nablamath.expression import parse_expr
from nablamath.formal import free_symbols, rule_lean_source, universal_lean_source
from nablamath.symbolic.rules import DEFAULT_EGRAPH_RULES

class UniversalLeanTranslationTests(unittest.TestCase):
    def test_preserves_variables_hypotheses_and_blocks_injection(self):
        source=universal_lean_source(parse_expr("x/x"),parse_expr("1"),
                                     nonzero=(parse_expr("x"),),theorem_name="div_self_generated")
        self.assertIn("(nabla_x : ℚ)",source); self.assertIn("(h0 : nabla_x ≠ 0)",source)
        self.assertIn("field_simp [h0]",source); self.assertNotIn("sorry",source)
        with self.assertRaises(ValueError):
            universal_lean_source(parse_expr("x"),parse_expr("x"),theorem_name="x := by sorry")
    def test_rule_hash_and_symbol_order(self):
        rule=next(r for r in DEFAULT_EGRAPH_RULES if r.name=="divide_self")
        self.assertIn(rule.rule_hash,rule_lean_source(rule))
        self.assertEqual(free_symbols(parse_expr("y+x*x")),("x","y"))

if __name__=="__main__": unittest.main()
