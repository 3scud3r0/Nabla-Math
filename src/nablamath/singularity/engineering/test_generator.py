"""Generate declarative boundary cases, not executable source strings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class TestCase:
    name: str
    inputs: Mapping[str, object]
    expected: object
    category: str


def boundary_cases(parameter: str, minimum: int, maximum: int) -> tuple[TestCase, ...]:
    if minimum > maximum:
        raise ValueError("Intervalo invertido")
    return (
        TestCase(f"{parameter}_below", {parameter: minimum - 1}, ValueError, "negative"),
        TestCase(f"{parameter}_minimum", {parameter: minimum}, "accepted", "boundary"),
        TestCase(f"{parameter}_maximum", {parameter: maximum}, "accepted", "boundary"),
        TestCase(f"{parameter}_above", {parameter: maximum + 1}, ValueError, "negative"),
    )


__all__ = ["TestCase", "boundary_cases"]
