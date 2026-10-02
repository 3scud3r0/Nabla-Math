import unittest
from pathlib import Path
from unittest.mock import patch

from nablamath.expression import parse_expr
from nablamath.formal.check import FormalCheck
from nablamath.formal.search import candidate_strategies, search_universal_proof


class FormalSearchTests(unittest.TestCase):
    def test_division_prioritizes_field_strategy(self):
        strategies = candidate_strategies(parse_expr("x/x"), parse_expr("1"), (parse_expr("x"),))
        self.assertEqual(strategies[0], "field_ring")
        self.assertEqual(len(strategies), len(set(strategies)))

    def test_search_records_rejection_then_kernel_acceptance(self):
        calls = []
        def fake_verify(source, content_id, project, timeout_s, success_detail):
            calls.append(source)
            ok = len(calls) == 2
            return FormalCheck(ok, "ok" if ok else "rejected", content_id)
        with patch("nablamath.formal.search._verify_source", side_effect=fake_verify):
            result = search_universal_proof(parse_expr("x+x"), parse_expr("2*x"), Path("."))
        self.assertTrue(result.verified)
        self.assertEqual(len(result.attempts), 2)
        self.assertFalse(result.attempts[0].verified)
        self.assertTrue(result.attempts[1].verified)
        self.assertNotIn("sorry", result.source)
        self.assertNotIn("axiom ", result.source)

    def test_unknown_tactic_text_cannot_enter_search_surface(self):
        strategies = candidate_strategies(parse_expr("x"), parse_expr("x"))
        self.assertNotIn("by sorry", strategies)


if __name__ == "__main__":
    unittest.main()