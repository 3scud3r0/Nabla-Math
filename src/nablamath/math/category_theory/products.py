"""Produtos categóricos em categorias finitas por propriedade universal."""

from dataclasses import dataclass

from .categories import FiniteCategory
from .limits import hom


@dataclass(frozen=True)
class ProductCone:
    product: str
    left_projection: str
    right_projection: str


def product_cones(category: FiniteCategory, left: str, right: str) -> tuple[ProductCone, ...]:
    if left not in category.objects or right not in category.objects: raise KeyError("objeto ausente")
    cones = []
    for candidate in category.objects:
        for left_projection in hom(category, candidate, left):
            for right_projection in hom(category, candidate, right):
                universal = True
                for source in category.objects:
                    for left_arrow in hom(category, source, left):
                        for right_arrow in hom(category, source, right):
                            mediators = [arrow for arrow in hom(category, source, candidate)
                                         if category.compose(left_projection, arrow) == left_arrow
                                         and category.compose(right_projection, arrow) == right_arrow]
                            if len(mediators) != 1:
                                universal = False; break
                        if not universal: break
                    if not universal: break
                if universal: cones.append(ProductCone(candidate, left_projection, right_projection))
    return tuple(cones)


__all__ = ["ProductCone", "product_cones"]
