from fractions import Fraction
import unittest

from nablamath.compiler import BackendUnavailable, compile_program, jax_available, lower_expr
from nablamath.expression import evaluate, parse_expr


class CompilerBackendTests(unittest.TestCase):
    def test_ir_is_deterministic_and_cse_reuses_nodes(self):
        expression = parse_expr("(x+y)*(x+y)")
        first = lower_expr(expression)
        second = lower_expr(expression)
        self.assertEqual(first.to_data(), second.to_data())
        self.assertEqual(first.content_id, second.content_id)
        plus_nodes = [i for i in first.instructions if i.op == "+"]
        self.assertEqual(len(plus_nodes), 1)

    def test_python_backend_preserves_exact_fraction_arithmetic(self):
        expression = parse_expr("(x+x)/3")
        program = lower_expr(expression)
        compiled = compile_program(program, backend="python")
        values = {"x": Fraction(5, 2)}
        self.assertEqual(compiled(values), evaluate(expression, values))

    def test_binding_is_strict(self):
        compiled = compile_program(lower_expr(parse_expr("x+y")))
        with self.assertRaises(ValueError):
            compiled({"x": 1})
        with self.assertRaises(ValueError):
            compiled({"x": 1, "y": 2, "z": 3})

    def test_jax_backend_is_optional_and_truthful(self):
        program = lower_expr(parse_expr("x*x+1"))
        if not jax_available():
            with self.assertRaises(BackendUnavailable):
                compile_program(program, backend="jax")
        else:
            compiled = compile_program(program, backend="jax", jit=False)
            value, gradient = compiled.value_and_grad({"x": 3.0}, "x")
            self.assertAlmostEqual(float(value), 10.0, places=5)
            self.assertAlmostEqual(float(gradient), 6.0, places=5)
            self.assertTrue(compiled.devices)


if __name__ == "__main__":
    unittest.main()