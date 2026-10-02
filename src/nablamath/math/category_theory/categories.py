"""Categorias pequenas finitas por tabelas explícitas."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping


@dataclass(frozen=True)
class Morphism:
    name: str
    source: str
    target: str
    def __post_init__(self) -> None:
        if not self.name or not self.source or not self.target: raise ValueError("morfismo inválido")


@dataclass(frozen=True)
class FiniteCategory:
    objects: tuple[str, ...]
    morphisms: tuple[Morphism, ...]
    identities: Mapping[str, str]
    composition: Mapping[tuple[str, str], str]  # (g,f) = g ∘ f

    def __post_init__(self) -> None:
        objects = set(self.objects)
        arrows = {arrow.name: arrow for arrow in self.morphisms}
        if not objects or len(objects) != len(self.objects) or len(arrows) != len(self.morphisms):
            raise ValueError("objetos ou morfismos duplicados/vazios")
        if any(arrow.source not in objects or arrow.target not in objects for arrow in self.morphisms):
            raise ValueError("morfismo referencia objeto ausente")
        if set(self.identities) != objects:
            raise ValueError("cada objeto requer identidade")
        for obj, name in self.identities.items():
            arrow = arrows.get(name)
            if arrow is None or arrow.source != obj or arrow.target != obj:
                raise ValueError("identidade inválida")
        expected = {(g.name, f.name) for f, g in product(self.morphisms, repeat=2) if f.target == g.source}
        if set(self.composition) != expected or any(name not in arrows for name in self.composition.values()):
            raise ValueError("composição deve cobrir exatamente os pares componíveis")
        for (g, f), result in self.composition.items():
            if arrows[result].source != arrows[f].source or arrows[result].target != arrows[g].target:
                raise ValueError("tipo da composição inválido")
        for arrow in self.morphisms:
            if self.compose(self.identities[arrow.target], arrow.name) != arrow.name or self.compose(arrow.name, self.identities[arrow.source]) != arrow.name:
                raise ValueError("lei da identidade violada")
        for f, g, h in product(self.morphisms, repeat=3):
            if f.target == g.source and g.target == h.source:
                if self.compose(h.name, self.compose(g.name, f.name)) != self.compose(self.compose(h.name, g.name), f.name):
                    raise ValueError("associatividade violada")

    def arrow(self, name: str) -> Morphism:
        for arrow in self.morphisms:
            if arrow.name == name: return arrow
        raise KeyError(name)

    def compose(self, g: str, f: str) -> str:
        try: return self.composition[g, f]
        except KeyError as exc: raise ValueError("morfismos não componíveis") from exc


def discrete_category(objects: tuple[str, ...]) -> FiniteCategory:
    morphisms = tuple(Morphism(f"id:{obj}", obj, obj) for obj in objects)
    identities = {obj: f"id:{obj}" for obj in objects}
    composition = {(name, name): name for name in identities.values()}
    return FiniteCategory(objects, morphisms, identities, composition)


__all__ = ["FiniteCategory", "Morphism", "discrete_category"]
