import unittest
from nablamath.autodiff import NamedTensor, Tensor, tensor_jacobian

class TensorAutodiffTests(unittest.TestCase):
    def test_broadcasting_gradient(self):
        x=Tensor([[1,2,3],[4,5,6]], requires_grad=True)
        b=Tensor([10,20,30], requires_grad=True)
        ((x+b)*2).sum().backward()
        self.assertEqual(x.grad, [[2.0,2.0,2.0],[2.0,2.0,2.0]])
        self.assertEqual(b.grad, [4.0,4.0,4.0])

    def test_matmul_gradient(self):
        a=Tensor([[1,2],[3,4]], requires_grad=True); b=Tensor([[5],[6]], requires_grad=True)
        (a@b).sum().backward()
        self.assertEqual(a.grad, [[5.0,6.0],[5.0,6.0]]); self.assertEqual(b.grad, [[4.0],[6.0]])

    def test_named_axes_and_jacobian(self):
        x=NamedTensor(Tensor([[1,2,3],[4,5,6]]), ("batch","feature"))
        b=NamedTensor(Tensor([10,20,30]), ("feature",))
        result=x+b
        self.assertEqual(result.axes, ("batch","feature"))
        self.assertEqual(result.tensor.tolist(), [[11.0,22.0,33.0],[14.0,25.0,36.0]])
        output, matrix=tensor_jacobian(lambda t:t*t, Tensor([2,3]))
        self.assertEqual(output.tolist(), [4.0,9.0]); self.assertEqual(matrix, ((4.0,0.0),(0.0,6.0)))

if __name__ == "__main__":
    unittest.main()
