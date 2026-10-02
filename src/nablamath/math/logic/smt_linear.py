"""Exact quantifier-free linear rational arithmetic via Fourier–Motzkin."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping


@dataclass(frozen=True)
class LinearInequality:
    """Represents ``sum(coefficients[name] * name) <= bound``."""

    coefficients: tuple[tuple[str, Fraction], ...]
    bound: Fraction

    def __init__(self, coefficients: Mapping[str, Fraction | int], bound: Fraction | int) -> None:
        canonical = tuple(sorted((name, Fraction(value)) for name, value in coefficients.items() if value))
        if any(not name.isidentifier() for name, _ in canonical):
            raise ValueError("Variável linear inválida")
        object.__setattr__(self, "coefficients", canonical)
        object.__setattr__(self, "bound", Fraction(bound))

    def coefficient(self, variable: str) -> Fraction:
        return dict(self.coefficients).get(variable, Fraction(0))


@dataclass(frozen=True)
class LinearSMTResult:
    satisfiable: bool
    eliminated_variables: tuple[str, ...]
    generated_constraints: int


def solve_linear_rational(inequalities: Iterable[LinearInequality], *,
                          constraint_limit: int = 100_000) -> LinearSMTResult:
    """Decide conjunctions of non-strict rational linear inequalities exactly."""
    if constraint_limit < 1:
        raise ValueError("constraint_limit deve ser positivo")
    constraints = list(dict.fromkeys(inequalities))
    variables = sorted({name for constraint in constraints for name, _ in constraint.coefficients})
    generated = 0
    eliminated: list[str] = []
    for variable in variables:
        positive, negative, zero = [], [], []
        for constraint in constraints:
            coefficient = constraint.coefficient(variable)
            (positive if coefficient > 0 else negative if coefficient < 0 else zero).append(constraint)
        next_constraints = list(zero)
        for upper in positive:
            for lower in negative:
                upper_coefficient = upper.coefficient(variable)
                lower_coefficient = lower.coefficient(variable)
                # (-lower_c)*upper + upper_c*lower cancels the variable.
                names = set(dict(upper.coefficients)) | set(dict(lower.coefficients))
                coefficients = {
                    name: (-lower_coefficient) * upper.coefficient(name)
                    + upper_coefficient * lower.coefficient(name)
                    for name in names if name != variable
                }
                bound = (-lower_coefficient) * upper.bound + upper_coefficient * lower.bound
                next_constraints.append(LinearInequality(coefficients, bound))
                generated += 1
                if generated > constraint_limit:
                    raise RuntimeError("Fourier-Motzkin excedeu o orçamento de restrições")
        constraints = list(dict.fromkeys(next_constraints))
        if any(not constraint.coefficients and constraint.bound < 0 for constraint in constraints):
            return LinearSMTResult(False, tuple((*eliminated, variable)), generated)
        eliminated.append(variable)
    satisfiable = not any(not constraint.coefficients and constraint.bound < 0
                          for constraint in constraints)
    return LinearSMTResult(satisfiable, tuple(eliminated), generated)


def equality(coefficients: Mapping[str, Fraction | int], value: Fraction | int) \
        -> tuple[LinearInequality, LinearInequality]:
    return (LinearInequality(coefficients, value),
            LinearInequality({name: -Fraction(coefficient)
                              for name, coefficient in coefficients.items()}, -Fraction(value)))


__all__ = ["LinearInequality", "LinearSMTResult", "equality", "solve_linear_rational"]
