"""Nó offline: ingestão por política, pins e snapshots; nenhum daemon ou rede."""

from __future__ import annotations

from pathlib import Path

from ..network.manifest import DatasetManifest
from ..network.objects import KnowledgeObject
from ..network.store import ContentStore
from .policies import IngestPolicy


class LocalNode:
    def __init__(self, root: str | Path, policy: IngestPolicy):
        root = Path(root)
        self.store = ContentStore(root / "objects")
        self.policy = policy
        self._pins_path = root / "pins"
        self._pins_path.mkdir(parents=True, exist_ok=True)

    def ingest(self, item: KnowledgeObject) -> str:
        self.policy.check(item, set(self.store.ids()))
        return self.store.put(item)

    def pin(self, object_id: str) -> None:
        if not self.store.contains(object_id):
            raise KeyError(object_id)
        (self._pins_path / object_id).touch(exist_ok=True)

    def unpin(self, object_id: str) -> None:
        try:
            (self._pins_path / object_id).unlink()
        except FileNotFoundError:
            pass

    def pinned_ids(self) -> tuple[str, ...]:
        return tuple(sorted(path.name for path in self._pins_path.iterdir()
                            if path.is_file() and self.store.contains(path.name)))

    def snapshot(self, name: str, selection_policy: str, license_summary: str, *,
                 license: str, provenance: dict[str, object]) -> KnowledgeObject:
        manifest = DatasetManifest(name, self.pinned_ids(), selection_policy, license_summary)
        return manifest.as_object(license=license, provenance=provenance)


__all__ = ["LocalNode"]
