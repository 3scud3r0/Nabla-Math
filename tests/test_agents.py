import unittest

from nablamath.agents import Proposal
from nablamath.agents.budget import Budget
from nablamath.agents.sandbox import run_untrusted_code
from nablamath.agents.trajectory import Trajectory


class AgentTests(unittest.TestCase):
    def test_rejects_malicious_code_and_records_rejected_attempt(self):
        path = Trajectory(Budget(max_proposals=2))
        self.assertIsNone(path.try_proposal(Proposal("__import__('os')", {}, "teste")))
        self.assertIsNotNone(path.try_proposal(Proposal("a+a", {"a": 3}, "dobrar")))
        self.assertEqual([attempt["status"] for attempt in path.attempts],
                         ["rejected", "accepted"])
        with self.assertRaises(ValueError):
            path.try_proposal(Proposal("1+1", {}, "terceira"))
        with self.assertRaises(PermissionError):
            run_untrusted_code("print('anything')")
