import unittest

from nablamath.gpu.batch_mcts_kernel import MCTSConfig, batch_mcts
from nablamath.gpu.cuda_f4_reduction import modular_rref
from nablamath.gpu.neural_guide import QuantizedLinearGuide
from nablamath.gpu.tensor_egraph import PackedENode, TensorEGraph
from nablamath.gpu.vram_buffer_manager import BufferManager


class GpuPrimitivesTests(unittest.TestCase):
    def test_buffer_manager_is_content_addressed_and_budgeted(self):
        with BufferManager(8) as manager:
            first = manager.put(b"abcd")
            second = manager.put(b"abcd")
            self.assertEqual(first, second)
            self.assertFalse(first.accelerated)
            self.assertEqual(manager.used_bytes, 4)
            self.assertEqual(manager.get(first), b"abcd")
            manager.release(first)
            self.assertEqual(manager.used_bytes, 4)
            manager.release(second)
            self.assertEqual(manager.used_bytes, 0)
            with self.assertRaises(MemoryError):
                manager.put(b"123456789")

    def test_modular_rref_is_exact_and_receipted(self):
        result = modular_rref(((1, 2, 3), (2, 4, 7)), 101)
        self.assertEqual(result.rank, 2)
        self.assertEqual(result.pivots, (0, 2))
        self.assertEqual(result.matrix, ((1, 2, 0), (0, 0, 1)))
        self.assertFalse(result.accelerated)
        self.assertEqual(len(result.content_id), 64)
        with self.assertRaises(ValueError):
            modular_rref(((1,),), 15)

    def test_tensor_egraph_batched_union_and_congruence(self):
        graph = TensorEGraph(4)
        self.assertEqual(graph.union_batch(((0, 1), (2, 3))), 2)
        self.assertEqual(graph.components(), ((0, 1), (2, 3)))
        self.assertEqual(graph.add_nodes((PackedENode(1, 0, 2), PackedENode(1, 1, 3))), 1)

    def test_quantized_guide_ranks_actions(self):
        guide = QuantizedLinearGuide.quantize(("expand", "factor"), ((1, -1), (-1, 1)))
        ranking = guide.rank((1, -1))
        self.assertEqual(ranking[0][0], "expand")
        self.assertGreater(ranking[0][1], ranking[1][1])

    def test_batched_mcts_finds_rewarding_action(self):
        result = batch_mcts(
            0,
            actions=lambda state: (1, 2) if state == 0 else (),
            transition=lambda state, action: action,
            terminal=lambda state: state != 0,
            evaluate=lambda states: [1.0 if state == 2 else 0.0 for state in states],
            config=MCTSConfig(simulations=64, batch_size=8, seed=4),
        )
        self.assertEqual(result.action, 2)
        self.assertEqual(result.simulations, 64)


if __name__ == "__main__":
    unittest.main()
