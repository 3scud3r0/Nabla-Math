import unittest

from nablamath.entity import ExpressionEntity
from nablamath.reports.solution import render_solution
from nablamath.solution import solve_expression


class SolutionReportTests(unittest.TestCase):
    def test_report_exposes_evidence_and_limitations(self):
        entity = ExpressionEntity.parse("x+0")
        bundle = solve_expression(entity, {"x": 2})
        source = render_solution(entity, bundle, {"x": 2})
        self.assertIn(entity.content_id, source)
        self.assertIn(bundle.content_id, source)
        self.assertIn("egraph", source)
        self.assertIn("not\\_requested", source)
        self.assertIn("Limitações", source)


if __name__ == "__main__":
    unittest.main()