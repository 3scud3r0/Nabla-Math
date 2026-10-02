"""Armazenamento local atômico e endereçado por conteúdo; sem transporte P2P."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Iterator

from .objects import KnowledgeObject


class ContentStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, object_id: str) -> Path:
        if len(object_id) != 64 or any(c not in "0123456789abcdef" for c in object_id):
            raise ValueError("identificador SHA-256 inválido")
        return self.root / object_id[:2] / object_id[2:]

    def put(self, item: KnowledgeObject) -> str:
        destination = self._path(item.object_id)
        if destination.exists():
            existing = self.get(item.object_id)
            if existing != item:
                raise ValueError("colisão ou objeto armazenado corrompido")
            return item.object_id
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".nabla-", dir=destination.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(item.to_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        return item.object_id

    def get(self, object_id: str) -> KnowledgeObject:
        path = self._path(object_id)
        try:
            item = KnowledgeObject.from_bytes(path.read_bytes())
        except FileNotFoundError as exc:
            raise KeyError(object_id) from exc
        if item.object_id != object_id:
            raise ValueError(f"integridade inválida para {object_id}")
        return item

    def contains(self, object_id: str) -> bool:
        return self._path(object_id).is_file()

    def ids(self) -> Iterator[str]:
        for directory in sorted(self.root.iterdir()):
            if directory.is_dir() and len(directory.name) == 2:
                for path in sorted(directory.iterdir()):
                    candidate = directory.name + path.name
                    try:
                        self._path(candidate)
                    except ValueError:
                        continue
                    if path.is_file() and not path.name.startswith("."):
                        yield candidate


__all__ = ["ContentStore"]
