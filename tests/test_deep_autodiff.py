import math
import unittest

from nablamath.autodiff import Tensor, Var


class DeepAutodiffTests(unittest.TestCase):
    def test_scalar_graph_exceeds_python_recursion_depth_safely(self):
        x = Var(1.0)
        y = x
        for _ in range(1500):
            y = y * 1.0001 + 0.0001
        y.backward()
        self.assertAlmostEqual(x.grad, 1.0001 ** 1500, places=10)

    def test_tensor_graph_exceeds_python_recursion_depth_safely(self):
        x = Tensor([1.0], requires_grad=True)
        y = x
        for _ in range(1200):
            y = y * 1.0001 + 0.0001
        y.sum().backward()
        self.assertAlmostEqual(x.grad[0], 1.0001 ** 1200, places=10)


if __name__ == "__main__":
    unittest.main()
