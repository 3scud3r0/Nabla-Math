"""Espaços topológicos finitos com verificação exaustiva dos axiomas."""

from dataclasses import dataclass

@dataclass(frozen=True)
class FiniteTopology:
    points: frozenset[str]
    open_sets: frozenset[frozenset[str]]

    def __post_init__(self) -> None:
        if not self.points or frozenset() not in self.open_sets or self.points not in self.open_sets:
            raise ValueError("vazio e espaço total devem ser abertos")
        if any(not subset <= self.points for subset in self.open_sets): raise ValueError("aberto contém ponto externo")
        opens = tuple(self.open_sets)
        for left in opens:
            for right in opens:
                if left | right not in self.open_sets: raise ValueError("união de abertos não é aberta")
                if left & right not in self.open_sets: raise ValueError("interseção finita não é aberta")

    def is_continuous_to(self, target: "FiniteTopology", mapping: dict[str, str]) -> bool:
        if set(mapping) != set(self.points) or any(value not in target.points for value in mapping.values()):
            raise ValueError("função não é total entre os espaços")
        return all(frozenset(point for point in self.points if mapping[point] in opened) in self.open_sets
                   for opened in target.open_sets)


__all__ = ["FiniteTopology"]
