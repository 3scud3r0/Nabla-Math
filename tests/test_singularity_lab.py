import unittest

from nablamath.singularity.core.cognition import Hypothesis, compare_hypothesis
from nablamath.singularity.core.memory import MemoryRecord, ResearchMemory
from nablamath.singularity.core.planner import Plan, Task
from nablamath.singularity.engineering.optimizer import Candidate, pareto_front
from nablamath.singularity.interfaces.api import ResearchAPI
from nablamath.singularity.interfaces.visualization import plan_to_dot
from nablamath.singularity.learning.evaluator import evaluate_against_baseline
from nablamath.singularity.system.configuration import LabConfiguration


class SingularityLabTests(unittest.TestCase):
    def test_hypothesis_evidence_is_explicit(self):
        hypothesis = Hypothesis("x+x=2*x", predictions=("p1", "p2", "p3"), confidence=.5)
        score = compare_hypothesis(hypothesis, {"p1": True, "p2": False})
        self.assertEqual((score.supported, score.contradicted, score.unknown), (1, 1, 1))
        self.assertEqual(score.score, 0)
        self.assertEqual(len(hypothesis.content_id), 64)

    def test_planner_rejects_cycles_and_orders_dependencies(self):
        tasks = (Task("a", "research", "pesquisar"),
                 Task("b", "mathematics", "formalizar", ("a",)))
        plan = Plan(tasks)
        self.assertEqual(plan.order, ("a", "b"))
        self.assertIn('"a" -> "b"', plan_to_dot(plan))
        with self.assertRaises(ValueError):
            Plan((Task("a", "research", "a", ("b",)),
                  Task("b", "research", "b", ("a",))))

    def test_memory_requires_existing_lineage(self):
        memory = ResearchMemory(2)
        root = MemoryRecord("hypothesis", {"text": "h"}, "proposal")
        root_id = memory.add(root)
        child = MemoryRecord("test", {"passed": True}, "tested", (root_id,))
        self.assertEqual(memory.get(memory.add(child)), child)
        with self.assertRaises(ValueError):
            ResearchMemory().add(MemoryRecord("bad", {}, "proposal", ("missing",)))

    def test_orchestrator_runs_bounded_review_pipeline(self):
        tasks = (
            Task("r", "research", "identidade"),
            Task("m", "mathematics", "formalizar", ("r",)),
            Task("c", "critique", "buscar contraexemplo", ("m",)),
            Task("e", "evaluate", "avaliar", ("c",)),
        )
        outcome = ResearchAPI(LabConfiguration(max_iterations=8)).run(tasks)
        self.assertEqual(outcome.completed, ("r", "m", "c", "e"))
        self.assertEqual(len(outcome.record_ids), 4)
        self.assertFalse(outcome.failures)
        self.assertTrue(all(proposal.requires_review for proposal in outcome.proposals))

    def test_evaluation_and_pareto_do_not_promote_dominated_work(self):
        evaluation = evaluate_against_baseline({"accuracy": .9}, {"accuracy": .8},
                                               {"accuracy": .05})
        self.assertTrue(evaluation.accepted)
        candidates = (Candidate("a", {"cost": 2, "accuracy": .9}),
                      Candidate("b", {"cost": 3, "accuracy": .8}))
        self.assertEqual(pareto_front(candidates, frozenset({"cost"})), (candidates[0],))

    def test_generated_code_execution_cannot_be_enabled(self):
        with self.assertRaises(ValueError):
            LabConfiguration(allow_generated_code_execution=True)


if __name__ == "__main__":
    unittest.main()
