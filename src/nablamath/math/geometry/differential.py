"""Polynomial differential forms with exact wedge and exterior derivative."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ..algebra.groebner import Polynomial

IndexSet = tuple[int, ...]


def _partial(polynomial: Polynomial, variable: int) -> Polynomial:
    terms = []
    for monomial, coefficient in polynomial.terms:
        exponent = monomial[variable]
        if exponent:
            reduced = list(monomial)
            reduced[variable] -= 1
            terms.append((tuple(reduced), coefficient * exponent))
    return Polynomial(polynomial.variables, terms)


def _wedge_indices(left: IndexSet, right: IndexSet) -> tuple[int, IndexSet] | None:
    if set(left) & set(right):
        return None
    inversions = sum(1 for first in left for second in right if first > second)
    return (-1 if inversions % 2 else 1), tuple(sorted(left + right))


@dataclass(frozen=True, init=False)
class DifferentialForm:
    variables: tuple[str, ...]
    degree: int
    components: tuple[tuple[IndexSet, Polynomial], ...]

    def __init__(self, variables: tuple[str, ...], degree: int,
                 components: Mapping[IndexSet, Polynomial]) -> None:
        if degree < 0:
            raise ValueError("Grau da forma inválido")
        if degree > len(variables) and components:
            raise ValueError("Somente a forma zero existe acima da dimensão")
        canonical = []
        for indices, coefficient in components.items():
            if tuple(sorted(indices)) != indices or len(indices) != degree or len(set(indices)) != degree:
                raise ValueError("Índices precisam ser estritamente crescentes")
            if any(not 0 <= index < len(variables) for index in indices):
                raise ValueError("Índice de diferencial fora da dimensão")
            if coefficient.variables != variables:
                raise ValueError("Coeficiente usa coordenadas diferentes")
            if not coefficient.is_zero:
                canonical.append((indices, coefficient))
        object.__setattr__(self, "variables", variables)
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "components", tuple(sorted(canonical)))

    def wedge(self, other: DifferentialForm) -> DifferentialForm:
        if self.variables != other.variables:
            raise ValueError("Formas usam coordenadas diferentes")
        result: dict[IndexSet, Polynomial] = {}
        for left_indices, left_coefficient in self.components:
            for right_indices, right_coefficient in other.components:
                combined = _wedge_indices(left_indices, right_indices)
                if combined is None:
                    continue
                sign, indices = combined
                result[indices] = result.get(indices, Polynomial.zero(self.variables)) \
                    + sign * left_coefficient * right_coefficient
        return DifferentialForm(self.variables, self.degree + other.degree, result)

    def exterior_derivative(self) -> DifferentialForm:
        if self.degree == len(self.variables):
            return DifferentialForm(self.variables, self.degree + 1, {})
        result: dict[IndexSet, Polynomial] = {}
        for indices, coefficient in self.components:
            for variable in range(len(self.variables)):
                derivative = _partial(coefficient, variable)
                combined = _wedge_indices((variable,), indices)
                if derivative.is_zero or combined is None:
                    continue
                sign, output_indices = combined
                result[output_indices] = result.get(output_indices, Polynomial.zero(self.variables)) \
                    + sign * derivative
        return DifferentialForm(self.variables, self.degree + 1, result)


def scalar_form(polynomial: Polynomial) -> DifferentialForm:
    return DifferentialForm(polynomial.variables, 0, {(): polynomial})


def coordinate_form(variables: tuple[str, ...], index: int) -> DifferentialForm:
    return DifferentialForm(variables, 1, {(index,): Polynomial.constant(variables, 1)})


__all__ = ["DifferentialForm", "coordinate_form", "scalar_form"]
