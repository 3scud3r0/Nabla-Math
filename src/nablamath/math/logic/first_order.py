"""Semântica finita de lógica de primeira ordem, sem parser ou cálculo de prova."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Mapping, Protocol

Element = str


@dataclass(frozen=True)
class Structure:
    universe: tuple[Element, ...]
    constants: Mapping[str, Element]
    functions: Mapping[str, tuple[int, Callable[..., Element]]]
    relations: Mapping[str, tuple[int, Callable[..., bool]]]

    def __post_init__(self) -> None:
        values = set(self.universe)
        if not values or len(values) != len(self.universe): raise ValueError("universo deve ser finito, não vazio e sem duplicatas")
        if any(value not in values for value in self.constants.values()): raise ValueError("constante fora do universo")
        for registry in (self.functions, self.relations):
            if any(not name or not isinstance(arity, int) or arity < 0 or not callable(operation)
                   for name, (arity, operation) in registry.items()): raise ValueError("símbolo inválido")
        for name, (arity, function) in self.functions.items():
            for arguments in product(self.universe, repeat=arity):
                if function(*arguments) not in values: raise ValueError(f"função {name} não é fechada")
        for name, (arity, relation) in self.relations.items():
            for arguments in product(self.universe, repeat=arity):
                if type(relation(*arguments)) is not bool: raise ValueError(f"relação {name} não retorna bool")


class Term(Protocol):
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element]) -> Element: ...

@dataclass(frozen=True)
class Variable:
    name: str
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element]) -> Element:
        if self.name not in assignment or assignment[self.name] not in structure.universe: raise ValueError(f"variável sem valor válido: {self.name}")
        return assignment[self.name]

@dataclass(frozen=True)
class Constant:
    name: str
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element]) -> Element:
        try: return structure.constants[self.name]
        except KeyError as exc: raise ValueError(f"constante desconhecida: {self.name}") from exc

@dataclass(frozen=True)
class Function:
    name: str
    arguments: tuple[Term, ...]
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element]) -> Element:
        try: arity, operation = structure.functions[self.name]
        except KeyError as exc: raise ValueError(f"função desconhecida: {self.name}") from exc
        if arity != len(self.arguments): raise ValueError("aridade de função incorreta")
        return operation(*(argument.evaluate(structure, assignment) for argument in self.arguments))


class Formula(Protocol):
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool: ...

@dataclass(frozen=True)
class Equal:
    left: Term
    right: Term
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool:
        values = assignment or {}; return self.left.evaluate(structure, values) == self.right.evaluate(structure, values)

@dataclass(frozen=True)
class Relation:
    name: str
    arguments: tuple[Term, ...]
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool:
        try: arity, predicate = structure.relations[self.name]
        except KeyError as exc: raise ValueError(f"relação desconhecida: {self.name}") from exc
        if arity != len(self.arguments): raise ValueError("aridade de relação incorreta")
        values = assignment or {}; return predicate(*(argument.evaluate(structure, values) for argument in self.arguments))

@dataclass(frozen=True)
class Negation:
    body: Formula
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool: return not self.body.evaluate(structure, assignment)

@dataclass(frozen=True)
class Conjunction:
    left: Formula
    right: Formula
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool: return self.left.evaluate(structure, assignment) and self.right.evaluate(structure, assignment)

@dataclass(frozen=True)
class ForAll:
    variable: str
    body: Formula
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool:
        base = dict(assignment or {})
        return all(self.body.evaluate(structure, {**base, self.variable: value}) for value in structure.universe)

@dataclass(frozen=True)
class Exists:
    variable: str
    body: Formula
    def evaluate(self, structure: Structure, assignment: Mapping[str, Element] | None = None) -> bool:
        base = dict(assignment or {})
        return any(self.body.evaluate(structure, {**base, self.variable: value}) for value in structure.universe)


__all__ = ["Conjunction", "Constant", "Equal", "Exists", "ForAll", "Function", "Negation", "Relation", "Structure", "Variable"]
