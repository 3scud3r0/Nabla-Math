import unittest
from fractions import Fraction

from nablamath.schema.units import KILOMETER, METER, Quantity, SECOND


class UnitContractTests(unittest.TestCase):
    def test_scale_is_exact(self):
        self.assertEqual(Quantity(Fraction(3, 2), KILOMETER).to(METER).value, Fraction(1500))

    def test_addition_preserves_left_unit(self):
        result = Quantity(1, METER) + Quantity(1, KILOMETER)
        self.assertEqual(result.unit, METER)
        self.assertEqual(result.value, 1001)

    def test_dimensions_block_invalid_conversion(self):
        with self.assertRaises(ValueError):
            Quantity(1, METER).to(SECOND)


if __name__ == "__main__":
    unittest.main()
