"""Funtores e transformações naturais entre categorias finitas."""

from dataclasses import dataclass
from typing import Mapping

from .categories import FiniteCategory


@dataclass(frozen=True)
class Functor:
    source: FiniteCategory
    target: FiniteCategory
    object_map: Mapping[str, str]
    morphism_map: Mapping[str, str]

    def __post_init__(self) -> None:
        if set(self.object_map) != set(self.source.objects) or set(self.morphism_map) != {a.name for a in self.source.morphisms}:
            raise ValueError("funtor deve mapear todos os objetos e morfismos")
        if any(value not in self.target.objects for value in self.object_map.values()): raise ValueError("objeto alvo inválido")
        for arrow in self.source.morphisms:
            image = self.target.arrow(self.morphism_map[arrow.name])
            if image.source != self.object_map[arrow.source] or image.target != self.object_map[arrow.target]:
                raise ValueError("funtor não preserva tipos")
        for obj, identity in self.source.identities.items():
            if self.morphism_map[identity] != self.target.identities[self.object_map[obj]]:
                raise ValueError("funtor não preserva identidades")
        for (g, f), composite in self.source.composition.items():
            if self.morphism_map[composite] != self.target.compose(self.morphism_map[g], self.morphism_map[f]):
                raise ValueError("funtor não preserva composição")


@dataclass(frozen=True)
class NaturalTransformation:
    source: Functor
    target: Functor
    components: Mapping[str, str]

    def __post_init__(self) -> None:
        if self.source.source != self.target.source or self.source.target != self.target.target:
            raise ValueError("funtores devem ter mesma origem e destino")
        category = self.source.source
        codomain = self.source.target
        if set(self.components) != set(category.objects): raise ValueError("componente ausente")
        for obj, name in self.components.items():
            arrow = codomain.arrow(name)
            if arrow.source != self.source.object_map[obj] or arrow.target != self.target.object_map[obj]:
                raise ValueError("componente com tipo incorreto")
        for arrow in category.morphisms:
            left = codomain.compose(self.components[arrow.target], self.source.morphism_map[arrow.name])
            right = codomain.compose(self.target.morphism_map[arrow.name], self.components[arrow.source])
            if left != right: raise ValueError("quadrado de naturalidade não comuta")


__all__ = ["Functor", "NaturalTransformation"]
