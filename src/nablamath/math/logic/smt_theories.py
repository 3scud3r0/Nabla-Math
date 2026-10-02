"""Exact, independently checkable building blocks for bounded SMT theories.

This module deliberately does not advertise a complete SMT solver.  It provides
the value semantics required for QF_BV and QF_AUFBV experiments, plus a complete
decision procedure for conjunctions of integer difference constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Hashable, Iterable, TypeVar


@dataclass(frozen=True)
class BitVector:
    """A fixed-width bit-vector with SMT-LIB compatible modular semantics."""

    width: int
    value: int

    def __post_init__(self) -> None:
        if self.width <= 0:
            raise ValueError("A largura deve ser positiva")
        object.__setattr__(self, "value", self.value & ((1 << self.width) - 1))

    def _compatible(self, other: BitVector) -> None:
        if self.width != other.width:
            raise ValueError("Bit-vectors possuem larguras diferentes")

    @property
    def signed(self) -> int:
        sign = 1 << (self.width - 1)
        return self.value - (1 << self.width) if self.value & sign else self.value

    def __add__(self, other: BitVector) -> BitVector:
        self._compatible(other)
        return BitVector(self.width, self.value + other.value)

    def __sub__(self, other: BitVector) -> BitVector:
        self._compatible(other)
        return BitVector(self.width, self.value - other.value)

    def __mul__(self, other: BitVector) -> BitVector:
        self._compatible(other)
        return BitVector(self.width, self.value * other.value)

    def __and__(self, other: BitVector) -> BitVector:
        self._compatible(other)
        return BitVector(self.width, self.value & other.value)

    def __or__(self, other: BitVector) -> BitVector:
        self._compatible(other)
        return BitVector(self.width, self.value | other.value)

    def __xor__(self, other: BitVector) -> BitVector:
        self._compatible(other)
        return BitVector(self.width, self.value ^ other.value)

    def __invert__(self) -> BitVector:
        return BitVector(self.width, ~self.value)

    def logical_shift_right(self, amount: int) -> BitVector:
        if amount < 0:
            raise ValueError("Deslocamento negativo")
        return BitVector(self.width, self.value >> amount)

    def arithmetic_shift_right(self, amount: int) -> BitVector:
        if amount < 0:
            raise ValueError("Deslocamento negativo")
        return BitVector(self.width, self.signed >> amount)

    def shift_left(self, amount: int) -> BitVector:
        if amount < 0:
            raise ValueError("Deslocamento negativo")
        return BitVector(self.width, self.value << amount)

    def unsigned_less_than(self, other: BitVector) -> bool:
        self._compatible(other)
        return self.value < other.value

    def signed_less_than(self, other: BitVector) -> bool:
        self._compatible(other)
        return self.signed < other.signed


Index = TypeVar("Index", bound=Hashable)
Value = TypeVar("Value")


@dataclass(frozen=True)
class ArrayValue(Generic[Index, Value]):
    """Persistent array value using a normalized finite store."""

    default: Value
    entries: tuple[tuple[Index, Value], ...] = ()

    def __post_init__(self) -> None:
        normalized: dict[Index, Value] = {}
        for index, value in self.entries:
            if value == self.default:
                normalized.pop(index, None)
            else:
                normalized[index] = value
        object.__setattr__(self, "entries", tuple(normalized.items()))

    def select(self, index: Index) -> Value:
        for candidate, value in reversed(self.entries):
            if candidate == index:
                return value
        return self.default

    def store(self, index: Index, value: Value) -> ArrayValue[Index, Value]:
        retained = tuple((candidate, current) for candidate, current in self.entries
                         if candidate != index)
        return ArrayValue(self.default, retained + ((index, value),))


@dataclass(frozen=True)
class DifferenceConstraint:
    """The integer constraint ``left - right <= bound``."""

    left: str
    right: str
    bound: int


@dataclass(frozen=True)
class DifferenceLogicResult:
    satisfiable: bool
    model: tuple[tuple[str, int], ...]
    negative_cycle: tuple[DifferenceConstraint, ...]


def solve_integer_difference_logic(
    constraints: Iterable[DifferenceConstraint],
) -> DifferenceLogicResult:
    """Decide an integer difference-logic conjunction using Bellman--Ford.

    Difference constraints have an integral model whenever they are feasible.
    The returned negative-cycle constraints form a machine-checkable UNSAT
    witness: summing them yields ``0 <=`` a negative integer.
    """
    items = tuple(constraints)
    variables = tuple(sorted({name for item in items for name in (item.left, item.right)}))
    distance = {name: 0 for name in variables}
    predecessor: dict[str, tuple[str, DifferenceConstraint]] = {}
    changed: str | None = None
    for _ in range(len(variables)):
        changed = None
        for item in items:
            candidate = distance[item.right] + item.bound
            if candidate < distance[item.left]:
                distance[item.left] = candidate
                predecessor[item.left] = (item.right, item)
                changed = item.left
        if changed is None:
            return DifferenceLogicResult(True, tuple(sorted(distance.items())), ())
    if changed is None:
        return DifferenceLogicResult(True, tuple(sorted(distance.items())), ())
    cursor = changed
    for _ in variables:
        cursor = predecessor[cursor][0]
    start = cursor
    cycle: list[DifferenceConstraint] = []
    while True:
        cursor, edge = predecessor[cursor]
        cycle.append(edge)
        if cursor == start:
            break
    return DifferenceLogicResult(False, (), tuple(cycle))


def verify_difference_result(constraints: Iterable[DifferenceConstraint],
                             result: DifferenceLogicResult) -> bool:
    """Independently verify either the integral model or negative-cycle proof."""
    items = tuple(constraints)
    if result.satisfiable:
        model = dict(result.model)
        return all(item.left in model and item.right in model
                   and model[item.left] - model[item.right] <= item.bound
                   for item in items)
    available = list(items)
    for edge in result.negative_cycle:
        if edge not in available:
            return False
        available.remove(edge)
    left = sorted(edge.left for edge in result.negative_cycle)
    right = sorted(edge.right for edge in result.negative_cycle)
    return (bool(result.negative_cycle) and left == right
            and sum(edge.bound for edge in result.negative_cycle) < 0)


__all__ = ["ArrayValue", "BitVector", "DifferenceConstraint", "DifferenceLogicResult",
           "solve_integer_difference_logic", "verify_difference_result"]
