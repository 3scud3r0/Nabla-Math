"""Fluxo máximo exato por Edmonds–Karp em redes racionais."""

from collections import deque
from fractions import Fraction
from typing import Mapping


def maximum_flow(vertices: frozenset[str], capacities: Mapping[tuple[str, str], int | Fraction],
                 source: str, sink: str) -> tuple[Fraction, dict[tuple[str, str], Fraction]]:
    if source == sink or source not in vertices or sink not in vertices: raise ValueError("fonte ou sorvedouro inválido")
    capacity = {(u, v): Fraction(value) for (u, v), value in capacities.items()}
    if any(u not in vertices or v not in vertices or u == v for u, v in capacity): raise ValueError("aresta inválida")
    if any(value < 0 for value in capacity.values()): raise ValueError("capacidade negativa")
    residual = dict(capacity)
    for u, v in tuple(capacity): residual.setdefault((v, u), Fraction())
    flow = {edge: Fraction() for edge in capacity}
    value = Fraction()
    while True:
        parent: dict[str, str | None] = {source: None}; queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in sorted(vertices):
                if v not in parent and residual.get((u, v), 0) > 0: parent[v] = u; queue.append(v)
        if sink not in parent: break
        path_capacity = None; v = sink
        while parent[v] is not None:
            u = parent[v]; available = residual[u, v]
            path_capacity = available if path_capacity is None else min(path_capacity, available); v = u
        assert path_capacity is not None
        v = sink
        while parent[v] is not None:
            u = parent[v]; residual[u, v] -= path_capacity; residual[v, u] = residual.get((v, u), 0) + path_capacity
            if (u, v) in flow: flow[u, v] += path_capacity
            else: flow[v, u] -= path_capacity
            v = u
        value += path_capacity
    return value, flow


__all__ = ["maximum_flow"]
