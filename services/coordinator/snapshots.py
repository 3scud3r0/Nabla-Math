"""Snapshot público verificável por Merkle root e manifesto."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from nablamath.coordination.merkle import merkle_root


@dataclass(frozen=True)
class Snapshot:
    version: str
    records: int
    merkle_root: str
    content_sha256: str
    visibility: str = "public"


def build(records: list[dict], version: str) -> Snapshot:
    if not version.strip():
        raise ValueError("versão requerida")
    canonical = "".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n" for item in records)
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    leaves = [hashlib.sha256(line.encode()).hexdigest() for line in canonical.splitlines()]
    return Snapshot(version, len(records), merkle_root(leaves), digest)
