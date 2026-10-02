"""Auditoria offline do armazenamento e de suas referências."""

from __future__ import annotations

from dataclasses import dataclass

from ..network.store import ContentStore


@dataclass(frozen=True)
class AuditReport:
    checked: int
    missing_dependencies: tuple[str, ...]
    corrupt_objects: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.missing_dependencies and not self.corrupt_objects


def audit_store(store: ContentStore) -> AuditReport:
    identifiers = tuple(store.ids())
    available = set(identifiers)
    missing: set[str] = set()
    corrupt: list[str] = []
    for identifier in identifiers:
        try:
            item = store.get(identifier)
        except ValueError:
            corrupt.append(identifier)
            continue
        missing.update(set(item.parents + item.dependencies) - available)
    return AuditReport(len(identifiers), tuple(sorted(missing)), tuple(sorted(corrupt)))


__all__ = ["AuditReport", "audit_store"]
