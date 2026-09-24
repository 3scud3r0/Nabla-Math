"""Conteúdo endereçado por SHA-256 com escrita atômica e conferência na leitura."""

from __future__ import annotations

from pathlib import Path
import hashlib
import os
import tempfile


class BlobStore:
    def __init__(self, root: Path):
        self.root = Path(root)

    def _path(self, digest: str) -> Path:
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Identificador SHA-256 inválido")
        return self.root / digest[:2] / digest

    def put(self, content: bytes) -> str:
        if len(content) > 64 * 1024 * 1024:
            raise ValueError("Blob excede 64 MiB")
        digest = hashlib.sha256(content).hexdigest()
        destination = self._path(digest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            self.get(digest)
            return digest
        name = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as output:
                name = output.name
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            os.replace(name, destination)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)
        return digest

    def get(self, digest: str) -> bytes:
        content = self._path(digest).read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("Blob corrompido")
        return content
