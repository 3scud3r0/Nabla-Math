"""Snapshots imutáveis de coleções; não equivalem a aprovação científica."""

from __future__ import annotations

from dataclasses import dataclass

from ..coordination.merkle import merkle_root
from .objects import KnowledgeObject


@dataclass(frozen=True)
class DatasetManifest:
    name: str
    object_ids: tuple[str, ...]
    selection_policy: str
    license_summary: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.selection_policy.strip() or not self.license_summary.strip():
            raise ValueError("manifesto requer nome, política de seleção e resumo de licenças")
        if not self.object_ids:
            raise ValueError("manifesto não pode ser vazio")
        if tuple(sorted(set(self.object_ids))) != self.object_ids:
            raise ValueError("IDs devem estar ordenados e sem duplicatas")
        merkle_root(list(self.object_ids))

    @property
    def root(self) -> str:
        return merkle_root(list(self.object_ids))

    def as_object(self, *, provenance: dict[str, object], license: str) -> KnowledgeObject:
        return KnowledgeObject(
            object_type="dataset_manifest",
            payload={
                "license_summary": self.license_summary,
                "merkle_root": self.root,
                "name": self.name,
                "object_ids": list(self.object_ids),
                "selection_policy": self.selection_policy,
            },
            provenance=provenance,
            license=license,
            dependencies=self.object_ids,
        )


__all__ = ["DatasetManifest"]
