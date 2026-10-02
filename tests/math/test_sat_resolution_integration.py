from fractions import Fraction
import unittest

from nablamath.expression import evaluate, parse_expr
from nablamath.math.logic.resolution import resolution_refutation, verify_resolution
from nablamath.math.logic.sat import normalize_cnf, solve_sat, verify_assignment
from nablamath.symbolic.integrate import integrate_polynomial


class AutomatedReasoningTests(unittest.TestCase):
    def test_dpll_handles_more_than_truth_table_limit_and_verifies_model(self):
        clauses = [({index, index + 1}) for index in range(1, 40)]
        clauses.append({1})
        result = solve_sat(clauses)
        assignment = dict(result.assignment)
        self.assertTrue(result.satisfiable)
        self.assertTrue(verify_assignment(normalize_cnf(clauses), assignment))
        self.assertGreaterEqual(len(assignment), 40)

    def test_dpll_detects_unsatisfiable_formula(self):
        result = solve_sat(({1}, {-1}))
        self.assertFalse(result.satisfiable)

    def test_resolution_proof_replays(self):
        clauses = normalize_cnf(({1, 2}, {-1}, {-2}))
        proof = resolution_refutation(clauses)
        self.assertTrue(proof.unsatisfiable)
        self.assertTrue(verify_resolution(clauses, proof))
        tampered = type(proof)(True, proof.steps[:-1])
        self.assertFalse(verify_resolution(clauses, tampered))

    def test_exact_polynomial_integration_certificate(self):
        source = parse_expr("3*x^2 + 2*x + 1/3")
        certificate = integrate_polynomial(source, "x")
        self.assertTrue(certificate.verify())
        self.assertEqual(evaluate(certificate.antiderivative, {"x": Fraction(2)}), Fraction(38, 3))
        self.assertTrue(certificate.to_data()["verified"])
        with self.assertRaises(ValueError):
            integrate_polynomial(parse_expr("1/x"), "x")


if __name__ == "__main__":
    unittest.main()
