"""Derivação para uma instância racional e suas condições."""

from fractions import Fraction
from typing import Mapping

from ..research import ResearchResult, calculate


def derive(source: str, values: Mapping[str, Fraction | int | str]) -> ResearchResult:
    return calculate(source, values)
