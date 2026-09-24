import unittest

from nablamath.research import calculate


class DomainRuleTests(unittest.TestCase):
    def test_cancel_requires_nonzero_value(self):
        result = calculate("(x*x)/x", {"x": 2})
        self.assertEqual(str(result.value), "2")
        self.assertTrue(result.nonzero)

    def test_zero_is_rejected_before_cancellation(self):
        with self.assertRaises(ValueError):
            calculate("(x*x)/x", {"x": 0})


if __name__ == "__main__":
    unittest.main()
