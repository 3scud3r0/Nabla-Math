from fractions import Fraction
import unittest

from nablamath.schema.units import HOUR, KILOMETER, KILOGRAM, METER, SECOND, Quantity


class UnitTests(unittest.TestCase):
    def test_exact_conversion_and_speed(self):
        self.assertEqual(Quantity(3, KILOMETER).to(METER).value, 3000)
        speed = Quantity(36, KILOMETER) / Quantity(1, HOUR)
        self.assertEqual(speed.to(METER / SECOND).value, 10)
        self.assertEqual((Quantity(1, METER) + Quantity(1, KILOMETER)).value, 1001)
        self.assertEqual((METER / SECOND**2).dimensions, (0, 1, -2))

    def test_incompatible_dimensions(self):
        with self.assertRaises(ValueError):
            Quantity(1, KILOGRAM).to(SECOND)
        with self.assertRaises(ValueError):
            Quantity(1, KILOGRAM) + Quantity(1, METER)
        with self.assertRaises(ZeroDivisionError):
            Quantity(1, METER) / Quantity(0, SECOND)
