"""Operações exatas em espaços topológicos finitos."""

from .general import FiniteTopology


def interior(space: FiniteTopology, subset: frozenset[str]) -> frozenset[str]:
    if not subset <= space.points: raise ValueError("subconjunto fora do espaço")
    return frozenset().union(*(opened for opened in space.open_sets if opened <= subset))


def closure(space: FiniteTopology, subset: frozenset[str]) -> frozenset[str]:
    if not subset <= space.points: raise ValueError("subconjunto fora do espaço")
    return space.points - interior(space, space.points - subset)


def boundary(space: FiniteTopology, subset: frozenset[str]) -> frozenset[str]:
    return closure(space, subset) - interior(space, subset)


def subspace(space: FiniteTopology, subset: frozenset[str]) -> FiniteTopology:
    if not subset or not subset <= space.points: raise ValueError("subespaço precisa ser não vazio e contido")
    return FiniteTopology(subset, frozenset(opened & subset for opened in space.open_sets))


def is_connected(space: FiniteTopology) -> bool:
    nontrivial = [opened for opened in space.open_sets if opened and opened != space.points]
    return not any(space.points - opened in space.open_sets for opened in nontrivial)


__all__ = ["boundary", "closure", "interior", "is_connected", "subspace"]
