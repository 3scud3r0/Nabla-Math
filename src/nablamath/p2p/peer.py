"""Descritores de peers; identidade autenticada continua sendo camada separada."""

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Peer:
    peer_id: str
    endpoint: str
    capabilities: frozenset[str]

    def __post_init__(self) -> None:
        if len(self.peer_id) != 64 or any(c not in "0123456789abcdef" for c in self.peer_id):
            raise ValueError("peer_id deve ser SHA-256")
        parsed = urlparse(self.endpoint)
        if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("endpoint de peer inválido")
        if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("peers remotos exigem HTTPS")
        allowed = {"objects", "bundles", "verification"}
        if not self.capabilities or not self.capabilities <= allowed:
            raise ValueError("capabilities inválidas")


__all__ = ["Peer"]
