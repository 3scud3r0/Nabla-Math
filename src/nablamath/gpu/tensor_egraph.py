"""Packed integer representation and batched congruence operations for e-graphs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PackedENode:
    opcode: int
    left: int
    right: int


class TensorEGraph:
    """Array-oriented union-find suitable for transfer to device backends.

    This class handles packed topology, not symbolic rule semantics.  It is a safe
    staging representation for accelerator kernels and provides a CPU oracle.
    """

    def __init__(self, class_count: int, *, class_limit: int = 10_000_000) -> None:
        if type(class_count) is not int or not 0 <= class_count <= class_limit:
            raise ValueError("class_count fora do orçamento")
        self.parent = list(range(class_count))
        self.rank = [0] * class_count
        self.nodes: list[PackedENode] = []
        self._node_keys: set[PackedENode] = set()

    def find(self, item: int) -> int:
        if type(item) is not int or not 0 <= item < len(self.parent):
            raise IndexError("e-class inexistente")
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while item != root:
            parent, self.parent[item] = self.parent[item], root
            item = parent
        return root

    def union(self, first: int, second: int) -> bool:
        first, second = self.find(first), self.find(second)
        if first == second:
            return False
        if self.rank[first] < self.rank[second] or (
            self.rank[first] == self.rank[second] and first > second
        ):
            first, second = second, first
        self.parent[second] = first
        if self.rank[first] == self.rank[second]:
            self.rank[first] += 1
        return True

    def union_batch(self, pairs: Iterable[tuple[int, int]]) -> int:
        changed = 0
        for first, second in pairs:
            changed += self.union(first, second)
        return changed

    def add_nodes(self, nodes: Iterable[PackedENode], *, node_limit: int = 10_000_000) -> int:
        added = 0
        for node in nodes:
            if node.opcode < 0:
                raise ValueError("Opcode precisa ser não negativo")
            canonical = PackedENode(node.opcode, self.find(node.left), self.find(node.right))
            if canonical in self._node_keys:
                continue
            if len(self.nodes) >= node_limit:
                raise MemoryError("Tensor e-graph excedeu o orçamento de nós")
            self.nodes.append(canonical)
            self._node_keys.add(canonical)
            added += 1
        return added

    def rebuild_congruence(self) -> int:
        """Merge owners of equal nodes; node index is also the owner when possible."""
        owners: dict[PackedENode, int] = {}
        merges = 0
        rebuilt: list[PackedENode] = []
        for index, node in enumerate(self.nodes):
            canonical = PackedENode(node.opcode, self.find(node.left), self.find(node.right))
            owner = min(index, len(self.parent) - 1) if self.parent else 0
            if canonical in owners and self.parent:
                merges += self.union(owner, owners[canonical])
            else:
                owners[canonical] = owner
            rebuilt.append(canonical)
        self.nodes = rebuilt
        self._node_keys = set(rebuilt)
        return merges

    def components(self) -> tuple[tuple[int, ...], ...]:
        groups: dict[int, list[int]] = {}
        for item in range(len(self.parent)):
            groups.setdefault(self.find(item), []).append(item)
        return tuple(tuple(groups[root]) for root in sorted(groups))


__all__ = ["PackedENode", "TensorEGraph"]
