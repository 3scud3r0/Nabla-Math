"""Propriedades universais elementares em categorias finitas."""

from .categories import FiniteCategory


def hom(category: FiniteCategory, source: str, target: str) -> tuple[str, ...]:
    if source not in category.objects or target not in category.objects: raise KeyError("objeto ausente")
    return tuple(sorted(arrow.name for arrow in category.morphisms if arrow.source == source and arrow.target == target))


def initial_objects(category: FiniteCategory) -> tuple[str, ...]:
    return tuple(obj for obj in category.objects if all(len(hom(category, obj, target)) == 1 for target in category.objects))


def terminal_objects(category: FiniteCategory) -> tuple[str, ...]:
    return tuple(obj for obj in category.objects if all(len(hom(category, source, obj)) == 1 for source in category.objects))


def is_isomorphism(category: FiniteCategory, morphism: str) -> bool:
    arrow = category.arrow(morphism)
    return any(category.compose(candidate.name, arrow.name) == category.identities[arrow.source]
               and category.compose(arrow.name, candidate.name) == category.identities[arrow.target]
               for candidate in category.morphisms
               if candidate.source == arrow.target and candidate.target == arrow.source)


__all__ = ["hom", "initial_objects", "is_isomorphism", "terminal_objects"]
