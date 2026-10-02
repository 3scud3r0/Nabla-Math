"""Fragmentação determinística para transporte; não implementa descoberta nem sockets."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class Chunk:
    index: int
    total: int
    payload: bytes
    sha256: str

    def __post_init__(self) -> None:
        if not 0 <= self.index < self.total or self.total < 1:
            raise ValueError("posição de chunk inválida")
        if hashlib.sha256(self.payload).hexdigest() != self.sha256:
            raise ValueError("hash do chunk inválido")


def split(raw: bytes, size: int = 256 * 1024) -> tuple[Chunk, ...]:
    if not raw or not 1 <= size <= 4 * 1024 * 1024:
        raise ValueError("conteúdo e tamanho de chunk devem respeitar os limites")
    payloads = [raw[offset:offset + size] for offset in range(0, len(raw), size)]
    return tuple(Chunk(index, len(payloads), payload, hashlib.sha256(payload).hexdigest())
                 for index, payload in enumerate(payloads))


def join(chunks: tuple[Chunk, ...], expected_sha256: str) -> bytes:
    if not chunks or tuple(chunk.index for chunk in chunks) != tuple(range(len(chunks))):
        raise ValueError("chunks ausentes ou fora de ordem")
    if any(chunk.total != len(chunks) for chunk in chunks):
        raise ValueError("total de chunks inconsistente")
    raw = b"".join(chunk.payload for chunk in chunks)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("conteúdo remontado não corresponde ao hash esperado")
    return raw


__all__ = ["Chunk", "join", "split"]
