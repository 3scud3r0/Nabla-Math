"""Grafos simples finitos e algoritmos estruturais determinísticos."""

from dataclasses import dataclass
from collections import deque


@dataclass(frozen=True)
class Graph:
    vertices: tuple[str, ...]
    edges: frozenset[frozenset[str]]

    def __post_init__(self) -> None:
        values = set(self.vertices)
        if len(values) != len(self.vertices): raise ValueError("vértices duplicados")
        for edge in self.edges:
            if len(edge) != 2 or not edge <= values: raise ValueError("aresta inválida")

    def neighbors(self, vertex: str) -> tuple[str, ...]:
        if vertex not in self.vertices: raise KeyError(vertex)
        return tuple(sorted(next(iter(edge - {vertex})) for edge in self.edges if vertex in edge))

    def shortest_path(self, source: str, target: str) -> tuple[str, ...] | None:
        if source not in self.vertices or target not in self.vertices: raise KeyError("vértice ausente")
        queue = deque([source]); parent = {source: None}
        while queue:
            current = queue.popleft()
            if current == target:
                path = []
                while current is not None: path.append(current); current = parent[current]
                return tuple(reversed(path))
            for neighbor in self.neighbors(current):
                if neighbor not in parent: parent[neighbor] = current; queue.append(neighbor)
        return None

    def components(self) -> tuple[tuple[str, ...], ...]:
        remaining = set(self.vertices); result = []
        while remaining:
            start = min(remaining); component = set(); queue = [start]
            while queue:
                current = queue.pop()
                if current in component: continue
                component.add(current); queue.extend(self.neighbors(current))
            remaining -= component; result.append(tuple(sorted(component)))
        return tuple(result)


__all__ = ["Graph"]
