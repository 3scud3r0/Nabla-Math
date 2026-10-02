"""Algoritmos para grafos dirigidos finitos representados por adjacência."""

from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar


Vertex = TypeVar("Vertex", bound=Hashable)


def normalize(graph: Mapping[Vertex, Iterable[Vertex]]) -> dict[Vertex, tuple[Vertex, ...]]:
    """Valida fechamento dos vértices e remove arestas duplicadas."""
    vertices = set(graph)
    if len(vertices) > 1_000_000:
        raise ValueError("grafo excede o limite")
    result: dict[Vertex, tuple[Vertex, ...]] = {}
    for vertex, neighbors in graph.items():
        unique = tuple(dict.fromkeys(neighbors))
        if any(neighbor not in vertices for neighbor in unique):
            raise ValueError("aresta referencia vértice ausente")
        result[vertex] = unique
    return result


def reverse(graph: Mapping[Vertex, Iterable[Vertex]]) -> dict[Vertex, tuple[Vertex, ...]]:
    normalized = normalize(graph)
    result: dict[Vertex, list[Vertex]] = {vertex: [] for vertex in normalized}
    for source, targets in normalized.items():
        for target in targets:
            result[target].append(source)
    return {vertex: tuple(neighbors) for vertex, neighbors in result.items()}


def topological_sort(graph: Mapping[Vertex, Iterable[Vertex]]) -> tuple[Vertex, ...]:
    """Retorna uma ordenação de Kahn ou rejeita ciclos."""
    normalized = normalize(graph)
    indegree = {vertex: 0 for vertex in normalized}
    for targets in normalized.values():
        for target in targets:
            indegree[target] += 1
    queue = deque(vertex for vertex in normalized if indegree[vertex] == 0)
    result = []
    while queue:
        vertex = queue.popleft()
        result.append(vertex)
        for target in normalized[vertex]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(result) != len(normalized):
        raise ValueError("grafo contém ciclo dirigido")
    return tuple(result)


def strongly_connected_components(
    graph: Mapping[Vertex, Iterable[Vertex]],
) -> tuple[frozenset[Vertex], ...]:
    """Calcula componentes fortemente conexas pelo algoritmo de Kosaraju."""
    normalized = normalize(graph)
    visited: set[Vertex] = set()
    finish: list[Vertex] = []

    for root in normalized:
        if root in visited:
            continue
        visited.add(root)
        stack: list[tuple[Vertex, int]] = [(root, 0)]
        while stack:
            vertex, index = stack[-1]
            neighbors = normalized[vertex]
            if index < len(neighbors):
                neighbor = neighbors[index]
                stack[-1] = (vertex, index + 1)
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, 0))
            else:
                finish.append(vertex)
                stack.pop()

    reversed_graph = reverse(normalized)
    visited.clear()
    components = []
    for root in reversed(finish):
        if root in visited:
            continue
        component: set[Vertex] = set()
        stack = [root]
        visited.add(root)
        while stack:
            vertex = stack.pop()
            component.add(vertex)
            for neighbor in reversed_graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        components.append(frozenset(component))
    return tuple(components)


def transitive_closure(
    graph: Mapping[Vertex, Iterable[Vertex]],
) -> dict[Vertex, frozenset[Vertex]]:
    """Retorna vértices alcançáveis por caminhos não vazios."""
    normalized = normalize(graph)
    result = {}
    for root in normalized:
        reachable: set[Vertex] = set()
        stack = list(normalized[root])
        while stack:
            vertex = stack.pop()
            if vertex in reachable:
                continue
            reachable.add(vertex)
            stack.extend(normalized[vertex])
        result[root] = frozenset(reachable)
    return result


__all__ = [
    "normalize",
    "reverse",
    "strongly_connected_components",
    "topological_sort",
    "transitive_closure",
]
