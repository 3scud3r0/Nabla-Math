"""Grafo local verificável de linhagem entre objetos armazenados."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from ..network.objects import KnowledgeObject


class KnowledgeGraph:
    def __init__(self, objects: Iterable[KnowledgeObject]):
        self.objects = {item.object_id: item for item in objects}
        self.children: dict[str, set[str]] = defaultdict(set)
        for item in self.objects.values():
            for dependency in (*item.parents, *item.dependencies):
                if dependency not in self.objects:
                    raise ValueError(f"dependência ausente: {dependency}")
                self.children[dependency].add(item.object_id)
        self._assert_acyclic()

    def _assert_acyclic(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(identifier: str) -> None:
            if identifier in visiting:
                raise ValueError("ciclo detectado no grafo de conhecimento")
            if identifier in visited:
                return
            visiting.add(identifier)
            item = self.objects[identifier]
            for dependency in (*item.parents, *item.dependencies):
                visit(dependency)
            visiting.remove(identifier)
            visited.add(identifier)

        for identifier in sorted(self.objects):
            visit(identifier)

    def ancestors(self, object_id: str) -> tuple[str, ...]:
        if object_id not in self.objects:
            raise KeyError(object_id)
        found: set[str] = set()
        pending = list(self.objects[object_id].parents + self.objects[object_id].dependencies)
        while pending:
            identifier = pending.pop()
            if identifier in found:
                continue
            found.add(identifier)
            item = self.objects[identifier]
            pending.extend(item.parents + item.dependencies)
        return tuple(sorted(found))

    def descendants(self, object_id: str) -> tuple[str, ...]:
        if object_id not in self.objects:
            raise KeyError(object_id)
        found: set[str] = set()
        pending = list(self.children[object_id])
        while pending:
            identifier = pending.pop()
            if identifier in found:
                continue
            found.add(identifier)
            pending.extend(self.children[identifier])
        return tuple(sorted(found))

    def retractions(self) -> dict[str, tuple[str, ...]]:
        result: dict[str, list[str]] = defaultdict(list)
        for item in self.objects.values():
            if item.object_type == "retraction":
                result[item.payload["target_id"]].append(item.object_id)
        return {target: tuple(sorted(receipts)) for target, receipts in result.items()}


__all__ = ["KnowledgeGraph"]
