"""Ordenação topológica e emparelhamento bipartido finitos."""

from collections import deque
from typing import Mapping


def topological_sort(vertices: frozenset[str], edges: frozenset[tuple[str, str]]) -> tuple[str, ...]:
    if any(left not in vertices or right not in vertices for left, right in edges): raise ValueError("aresta com vértice ausente")
    indegree = {vertex: 0 for vertex in vertices}; outgoing = {vertex: [] for vertex in vertices}
    for left, right in edges: outgoing[left].append(right); indegree[right] += 1
    ready = sorted(vertex for vertex, degree in indegree.items() if degree == 0); result = []
    while ready:
        vertex = ready.pop(0); result.append(vertex)
        for target in sorted(outgoing[vertex]):
            indegree[target] -= 1
            if indegree[target] == 0: ready.append(target); ready.sort()
    if len(result) != len(vertices): raise ValueError("grafo contém ciclo dirigido")
    return tuple(result)


def maximum_bipartite_matching(left: frozenset[str], right: frozenset[str],
                               edges: frozenset[tuple[str, str]]) -> dict[str, str]:
    if left & right: raise ValueError("partições devem ser disjuntas")
    if any(a not in left or b not in right for a, b in edges): raise ValueError("aresta fora das partições")
    adjacency = {vertex: sorted(b for a, b in edges if a == vertex) for vertex in left}
    matched_right: dict[str, str] = {}
    def augment(vertex: str, visited: set[str]) -> bool:
        for target in adjacency[vertex]:
            if target in visited: continue
            visited.add(target)
            if target not in matched_right or augment(matched_right[target], visited):
                matched_right[target] = vertex; return True
        return False
    for vertex in sorted(left): augment(vertex, set())
    return {source: target for target, source in sorted(matched_right.items(), key=lambda pair: pair[1])}


__all__ = ["maximum_bipartite_matching", "topological_sort"]
