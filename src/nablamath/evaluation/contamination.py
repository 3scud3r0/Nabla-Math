"""Detecção conservadora de vazamento por componentes de proveniência."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from ..network.objects import KnowledgeObject


def provenance_components(objects: Iterable[KnowledgeObject]) -> dict[str, str]:
    items = {item.object_id: item for item in objects}
    parent = {identifier: identifier for identifier in items}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    origins: dict[str, list[str]] = defaultdict(list)
    for identifier, item in items.items():
        source = item.provenance.get("source_id")
        if isinstance(source, str):
            origins[source].append(identifier)
        for related in item.parents + item.dependencies:
            if related in items:
                union(identifier, related)
    for members in origins.values():
        for member in members[1:]:
            union(members[0], member)
    return {identifier: find(identifier) for identifier in sorted(items)}


def leakage(train_ids: Iterable[str], evaluation_ids: Iterable[str], components: dict[str, str]) -> tuple[str, ...]:
    train_components = {components[item] for item in train_ids if item in components}
    return tuple(sorted(item for item in evaluation_ids
                        if item in components and components[item] in train_components))


__all__ = ["leakage", "provenance_components"]
