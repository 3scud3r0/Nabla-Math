import unittest

from nablamath.formal import lean_source
from nablamath.research import calculate


class LeanSourceTests(unittest.TestCase):
    def test_instance_has_no_trust_shortcuts(self):
        source = lean_source(calculate("(x+x)/x", {"x": 3}))
        self.assertIn("import Mathlib", source)
        self.assertIn("norm_num", source)
        self.assertNotIn("sorry", source)
        self.assertNotIn("axiom ", source)

    def test_source_values_are_numbers_not_code(self):
        with self.assertRaises(ValueError):
            calculate("x", {"x": "0); #eval IO.println 1"})
        source = lean_source(calculate("(x+1)**-1", {"x": "1/2"}))
        self.assertIn("⁻¹", source)
