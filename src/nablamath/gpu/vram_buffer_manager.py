"""Budgeted device-buffer residency without pretending a CPU is a GPU."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Protocol


class BufferBackend(Protocol):
    name: str
    accelerated: bool

    def allocate(self, size: int) -> object: ...
    def write(self, buffer: object, data: bytes) -> None: ...
    def read(self, buffer: object, size: int) -> bytes: ...
    def release(self, buffer: object) -> None: ...


class CpuBufferBackend:
    """Reference backend used for tests and machines without an accelerator."""

    name = "cpu-bytearray"
    accelerated = False

    def allocate(self, size: int) -> bytearray:
        return bytearray(size)

    def write(self, buffer: object, data: bytes) -> None:
        if not isinstance(buffer, bytearray):
            raise TypeError("CpuBufferBackend recebeu buffer incompatível")
        buffer[:len(data)] = data

    def read(self, buffer: object, size: int) -> bytes:
        if not isinstance(buffer, bytearray):
            raise TypeError("CpuBufferBackend recebeu buffer incompatível")
        return bytes(buffer[:size])

    def release(self, buffer: object) -> None:
        if isinstance(buffer, bytearray):
            buffer.clear()


@dataclass(frozen=True)
class BufferHandle:
    identifier: str
    size_bytes: int
    sha256: str
    backend: str
    accelerated: bool


class BufferManager:
    """Own device allocations under a hard byte budget.

    Deduplication is content-addressed.  Handles become invalid immediately after
    release; callers never receive the backend's mutable allocation object.
    """

    def __init__(self, capacity_bytes: int, backend: BufferBackend | None = None) -> None:
        if type(capacity_bytes) is not int or capacity_bytes < 1:
            raise ValueError("capacity_bytes deve ser inteiro positivo")
        self.capacity_bytes = capacity_bytes
        self.backend = backend or CpuBufferBackend()
        self._allocations: dict[str, tuple[object, BufferHandle, int]] = {}
        self._used_bytes = 0

    @property
    def used_bytes(self) -> int:
        return self._used_bytes

    @property
    def available_bytes(self) -> int:
        return self.capacity_bytes - self._used_bytes

    def put(self, data: bytes) -> BufferHandle:
        if not isinstance(data, bytes):
            raise TypeError("BufferManager aceita bytes imutáveis")
        digest = hashlib.sha256(data).hexdigest()
        if digest in self._allocations:
            allocation, handle, references = self._allocations[digest]
            self._allocations[digest] = (allocation, handle, references + 1)
            return handle
        if len(data) > self.available_bytes:
            raise MemoryError("Orçamento do dispositivo excedido")
        allocation = self.backend.allocate(len(data))
        try:
            self.backend.write(allocation, data)
        except BaseException:
            self.backend.release(allocation)
            raise
        handle = BufferHandle(digest, len(data), digest, self.backend.name,
                              bool(self.backend.accelerated))
        self._allocations[digest] = (allocation, handle, 1)
        self._used_bytes += len(data)
        return handle

    def get(self, handle: BufferHandle) -> bytes:
        record = self._allocations.get(handle.identifier)
        if record is None or record[1] != handle:
            raise KeyError("Handle de buffer ausente ou obsoleto")
        data = self.backend.read(record[0], handle.size_bytes)
        if hashlib.sha256(data).hexdigest() != handle.sha256:
            raise RuntimeError("Corrupção detectada no buffer residente")
        return data

    def release(self, handle: BufferHandle) -> None:
        record = self._allocations.get(handle.identifier)
        if record is None or record[1] != handle:
            raise KeyError("Handle de buffer ausente ou obsoleto")
        allocation, _, references = record
        if references > 1:
            self._allocations[handle.identifier] = (allocation, handle, references - 1)
            return
        self.backend.release(allocation)
        del self._allocations[handle.identifier]
        self._used_bytes -= handle.size_bytes

    def close(self) -> None:
        for allocation, _, _ in self._allocations.values():
            self.backend.release(allocation)
        self._allocations.clear()
        self._used_bytes = 0

    def __enter__(self) -> BufferManager:
        return self

    def __exit__(self, *ignored: object) -> None:
        self.close()


__all__ = ["BufferBackend", "BufferHandle", "BufferManager", "CpuBufferBackend"]
