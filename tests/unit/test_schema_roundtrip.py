import unittest

from nablamath.expression import parse_expr, to_data
from nablamath.schema.expression import from_data


class SchemaRoundTripTests(unittest.TestCase):
    def test_ast_roundtrip_is_exact(self):
        expression = parse_expr("(x+2)/3")
        self.assertEqual(to_data(from_data(to_data(expression))), to_data(expression))

    def test_unknown_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            from_data({"kind": "symbol", "name": "x", "extra": 1})


if __name__ == "__main__":
    unittest.main()
