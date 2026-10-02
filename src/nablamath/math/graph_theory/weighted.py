"""Grafos dirigidos ponderados com pesos racionais não negativos."""

from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from typing import Mapping


@dataclass(frozen=True)
class WeightedDigraph:
    vertices: frozenset[str]
    weights: Mapping[tuple[str, str], Fraction]

    def __post_init__(self) -> None:
        normalized = {(source, target): Fraction(weight) for (source, target), weight in self.weights.items()}
        if not self.vertices: raise ValueError("grafo vazio")
        if any(source not in self.vertices or target not in self.vertices for source, target in normalized): raise ValueError("aresta com vértice ausente")
        if any(weight < 0 for weight in normalized.values()): raise ValueError("Dijkstra exige pesos não negativos")
        object.__setattr__(self, "weights", normalized)

    def shortest_distances(self, source: str) -> dict[str, Fraction | None]:
        if source not in self.vertices: raise KeyError(source)
        distances = {source: Fraction()}; queue = [(Fraction(), source)]
        adjacency: dict[str, list[tuple[str, Fraction]]] = {vertex: [] for vertex in self.vertices}
        for (left, right), weight in self.weights.items(): adjacency[left].append((right, weight))
        while queue:
            distance, vertex = heappop(queue)
            if distance != distances.get(vertex): continue
            for target, weight in sorted(adjacency[vertex]):
                candidate = distance + weight
                if target not in distances or candidate < distances[target]:
                    distances[target] = candidate; heappush(queue, (candidate, target))
        return {vertex: distances.get(vertex) for vertex in sorted(self.vertices)}


__all__ = ["WeightedDigraph"]
