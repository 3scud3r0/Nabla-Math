import unittest

from nablamath.agents import Proposal
from nablamath.agents.budget import Budget
from nablamath.agents.sandbox import run_untrusted_code
from nablamath.agents.protocol import execute_proposal


class AgentLimitTests(unittest.TestCase):
    def test_untrusted_code_fails_closed(self):
        with self.assertRaises(PermissionError):
            run_untrusted_code("open('/etc/passwd').read()")

    def test_proposal_budget_is_enforced(self):
        with self.assertRaises(ValueError):
            execute_proposal(Proposal("1+1", {}, ""), Budget())


if __name__ == "__main__":
    unittest.main()
