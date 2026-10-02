import math
import unittest
from nablamath.autodiff import Var, exp, hessian, jacobian, jvp, value_and_grad, vjp

class ReverseAutodiffTests(unittest.TestCase):
    def test_forward_compatibility(self):
        primal, tangent = jvp(lambda x: x*x + 3*x, 2.0)
        self.assertAlmostEqual(primal, 10.0); self.assertAlmostEqual(tangent, 7.0)

    def test_reverse_gradient_vjp_and_jacobian(self):
        _, gradient = value_and_grad(lambda x, y: x*x*y + exp(y), 2.0, 0.5)
        self.assertAlmostEqual(gradient[0], 2.0)
        self.assertAlmostEqual(gradient[1], 4.0 + math.exp(0.5))
        value, pullback = vjp(lambda x, y: x*y, [3.0, 4.0], cotangent=2.0)
        self.assertEqual((value, pullback), (12.0, (8.0, 6.0)))
        values, matrix = jacobian(lambda x, y: (x*y, x+y), [2.0, 3.0])
        self.assertEqual(values, (6.0, 5.0)); self.assertEqual(matrix, ((3.0, 2.0), (1.0, 1.0)))

    def test_hessian(self):
        value, gradient, matrix = hessian(lambda x, y: x*x*y + y**3, [2.0, 3.0])
        self.assertEqual(value, 39.0); self.assertEqual(gradient, (12.0, 31.0))
        self.assertEqual(matrix, ((6.0, 4.0), (4.0, 18.0)))

    def test_backward_resets_gradients(self):
        x=Var(2.0); y=x*x; y.backward(); self.assertEqual(x.grad, 4.0)
        y.backward(); self.assertEqual(x.grad, 4.0)

if __name__ == "__main__":
    unittest.main()
