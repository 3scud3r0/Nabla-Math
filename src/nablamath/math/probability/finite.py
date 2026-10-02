"""Espaços de probabilidade finitos com pesos racionais exatos."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Generic, Mapping, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class FiniteDistribution(Generic[T]):
    masses: Mapping[T, Fraction]

    def __post_init__(self) -> None:
        normalized = {outcome: Fraction(mass) for outcome, mass in self.masses.items()}
        if not normalized or any(mass < 0 for mass in normalized.values()) or sum(normalized.values()) != 1:
            raise ValueError("massas devem ser não negativas e somar exatamente um")
        object.__setattr__(self, "masses", normalized)

    def probability(self, predicate: Callable[[T], bool]) -> Fraction:
        return sum((mass for outcome, mass in self.masses.items() if predicate(outcome)), Fraction())

    def expectation(self, variable: Callable[[T], int | Fraction]) -> Fraction:
        return sum((mass * Fraction(variable(outcome)) for outcome, mass in self.masses.items()), Fraction())

    def variance(self, variable: Callable[[T], int | Fraction]) -> Fraction:
        mean = self.expectation(variable)
        return sum((mass * (Fraction(variable(outcome)) - mean) ** 2 for outcome, mass in self.masses.items()), Fraction())

    def condition(self, predicate: Callable[[T], bool]) -> "FiniteDistribution[T]":
        probability = self.probability(predicate)
        if probability == 0: raise ValueError("não é possível condicionar em evento nulo")
        return FiniteDistribution({outcome: mass / probability for outcome, mass in self.masses.items() if predicate(outcome)})


__all__ = ["FiniteDistribution"]
