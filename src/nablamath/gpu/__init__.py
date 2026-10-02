"""Optional accelerator-neutral primitives with deterministic CPU fallbacks.

No function in this package claims CUDA execution unless the supplied backend
reports an accelerator device.  Exact arithmetic remains on integer prime fields.
"""

from .batch_mcts_kernel import MCTSConfig, MCTSResult, batch_mcts
from .cuda_f4_reduction import F4ReductionResult, modular_rref
from .neural_guide import QuantizedLinearGuide
from .tensor_egraph import TensorEGraph
from .vram_buffer_manager import BufferHandle, BufferManager, CpuBufferBackend

__all__ = [
    "BufferHandle", "BufferManager", "CpuBufferBackend", "F4ReductionResult",
    "MCTSConfig", "MCTSResult", "QuantizedLinearGuide", "TensorEGraph",
    "batch_mcts", "modular_rref",
]
