import unittest

from nablamath.coordination.merkle import merkle_root


class MerkleTests(unittest.TestCase):
    def test_order_independence_change_detection(self):
        a, b, c = (letter*64 for letter in "abc")
        self.assertEqual(merkle_root([a,b]), merkle_root([b,a]))
        self.assertNotEqual(merkle_root([a,b]), merkle_root([a,c]))
        with self.assertRaises(ValueError):
            merkle_root([a,a])
