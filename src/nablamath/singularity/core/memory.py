"""Content-addressed bounded episodic memory with explicit evidence status."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Literal, Mapping

EvidenceState = Literal["proposal", "tested", "verified", "refuted", "retracted"]


@dataclass(frozen=True)
class MemoryRecord:
    kind: str
    payload: Mapping[str, object]
    state: EvidenceState
    parents: tuple[str, ...] = ()

    @property
    def content_id(self) -> str:
        canonical = json.dumps({"kind": self.kind, "payload": self.payload, "state": self.state,
                                "parents": self.parents}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


class ResearchMemory:
    def __init__(self, limit: int = 10_000) -> None:
        if limit < 1:
            raise ValueError("limit deve ser positivo")
        self.limit = limit
        self._records: dict[str, MemoryRecord] = {}

    def add(self, record: MemoryRecord) -> str:
        identifier = record.content_id
        missing = set(record.parents) - set(self._records)
        if missing:
            raise ValueError(f"Memória referencia pais ausentes: {sorted(missing)}")
        if identifier not in self._records and len(self._records) >= self.limit:
            raise MemoryError("Memória de pesquisa atingiu o limite")
        self._records[identifier] = record
        return identifier

    def get(self, identifier: str) -> MemoryRecord:
        return self._records[identifier]

    def by_state(self, state: EvidenceState) -> tuple[MemoryRecord, ...]:
        return tuple(record for _, record in sorted(self._records.items()) if record.state == state)

    def __len__(self) -> int:
        return len(self._records)


__all__ = ["EvidenceState", "MemoryRecord", "ResearchMemory"]
