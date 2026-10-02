"""Recibos declarativos de verificação, sem alegação automática de verdade."""

from __future__ import annotations

from dataclasses import dataclass

from .objects import KnowledgeObject

METHODS = frozenset({"exact_reexecution", "independent_implementation", "formal_kernel", "human_review", "external_reference"})
OUTCOMES = frozenset({"passed", "failed", "inconclusive"})


def _digest(value: str, label: str) -> None:
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{label} deve ser um SHA-256")


@dataclass(frozen=True)
class VerificationReceipt:
    subject_id: str
    verifier: str
    method: str
    outcome: str
    evidence_ids: tuple[str, ...]
    environment_id: str
    statement: str

    def __post_init__(self) -> None:
        _digest(self.subject_id, "subject_id")
        _digest(self.environment_id, "environment_id")
        if not self.verifier.strip() or not self.statement.strip():
            raise ValueError("verificador e declaração são obrigatórios")
        if self.method not in METHODS or self.outcome not in OUTCOMES:
            raise ValueError("método ou resultado não suportado")
        if tuple(sorted(set(self.evidence_ids))) != self.evidence_ids:
            raise ValueError("evidências devem estar ordenadas e sem duplicatas")
        for item in self.evidence_ids:
            _digest(item, "evidence_id")

    def as_object(self, *, license: str, provenance: dict[str, object]) -> KnowledgeObject:
        dependencies = tuple(sorted(set((self.subject_id, self.environment_id, *self.evidence_ids))))
        return KnowledgeObject(
            object_type="verification_receipt", license=license, provenance=provenance,
            dependencies=dependencies,
            payload={"subject_id": self.subject_id, "verifier": self.verifier,
                     "method": self.method, "outcome": self.outcome,
                     "evidence_ids": list(self.evidence_ids),
                     "environment_id": self.environment_id, "statement": self.statement},
        )


__all__ = ["METHODS", "OUTCOMES", "VerificationReceipt"]
