import unittest
from pathlib import Path

from nablamath.formal import FormalCheck, lean_source, verify_with_lean
from nablamath.research import calculate


class LeanBridgeTests(unittest.TestCase):
    def test_translation_is_closed_and_restricted(self):
        source = lean_source(calculate("(x+x)/x", {"x": 3}))
        self.assertIn("norm_num", source)
        self.assertNotIn("sorry", source)

    def test_missing_project_is_explicit_error(self):
        with self.assertRaises(ValueError):
            verify_with_lean(calculate("1+1", {}), Path("/tmp/not-a-lean-project"))


if __name__ == "__main__":
    unittest.main()
