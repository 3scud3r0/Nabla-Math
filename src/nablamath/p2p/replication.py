"""Planejamento e ingestão de replicação; transporte permanece injetado pelo chamador."""

from __future__ import annotations

from collections.abc import Iterable

from ..network.objects import KnowledgeObject
from ..node.local import LocalNode


def missing(local_ids: Iterable[str], remote_ids: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(remote_ids) - set(local_ids)))


def ingest_batch(node: LocalNode, objects: Iterable[KnowledgeObject]) -> tuple[str, ...]:
    pending = {item.object_id: item for item in objects}
    accepted: list[str] = []
    while pending:
        progress = False
        available = set(node.store.ids())
        for identifier, item in sorted(tuple(pending.items())):
            if set(item.dependencies) <= available:
                node.ingest(item)
                accepted.append(identifier)
                del pending[identifier]
                progress = True
        if not progress:
            unresolved = ",".join(sorted(pending))
            raise ValueError(f"lote possui dependências ausentes ou cíclicas: {unresolved}")
    return tuple(accepted)


__all__ = ["ingest_batch", "missing"]
