"""Compromisso de avaliação: publica hash e metadados, não o conteúdo selado."""

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class SealedEvaluation:
    commitment: str
    item_count: int
    policy: str

    @classmethod
    def commit(cls, raw: bytes, *, item_count: int, policy: str) -> "SealedEvaluation":
        if not raw or item_count < 1 or not policy.strip():
            raise ValueError("avaliação selada inválida")
        return cls(hashlib.sha256(raw).hexdigest(), item_count, policy)

    def verify(self, raw: bytes) -> bool:
        return hashlib.sha256(raw).hexdigest() == self.commitment


__all__ = ["SealedEvaluation"]
