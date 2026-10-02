"""Distribuições conjuntas finitas e independência exata."""

from fractions import Fraction
from typing import TypeVar

from .finite import FiniteDistribution

A = TypeVar("A"); B = TypeVar("B")


def first_marginal(distribution: FiniteDistribution[tuple[A, B]]) -> FiniteDistribution[A]:
    masses: dict[A, Fraction] = {}
    for (left, _), mass in distribution.masses.items(): masses[left] = masses.get(left, Fraction()) + mass
    return FiniteDistribution(masses)


def second_marginal(distribution: FiniteDistribution[tuple[A, B]]) -> FiniteDistribution[B]:
    masses: dict[B, Fraction] = {}
    for (_, right), mass in distribution.masses.items(): masses[right] = masses.get(right, Fraction()) + mass
    return FiniteDistribution(masses)


def independent(distribution: FiniteDistribution[tuple[A, B]]) -> bool:
    left, right = first_marginal(distribution), second_marginal(distribution)
    return all(distribution.masses.get((a, b), Fraction()) == left.masses[a] * right.masses[b]
               for a in left.masses for b in right.masses)


def product_distribution(left: FiniteDistribution[A], right: FiniteDistribution[B]) -> FiniteDistribution[tuple[A, B]]:
    return FiniteDistribution({(a, b): pa * pb for a, pa in left.masses.items() for b, pb in right.masses.items()})


__all__ = ["first_marginal", "independent", "product_distribution", "second_marginal"]
