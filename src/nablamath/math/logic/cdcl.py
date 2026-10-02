"""Deterministic CDCL SAT with clause learning, VSIDS-like activity and restarts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .sat import CNF, normalize_cnf, verify_assignment


@dataclass(frozen=True)
class CDCLResult:
    satisfiable: bool
    assignment: tuple[tuple[int, bool], ...]
    decisions: int
    conflicts: int
    learned_clauses: int
    restarts: int


def solve_cdcl(clauses: Iterable[Iterable[int]], *, conflict_limit: int = 1_000_000,
               restart_interval: int = 100) -> CDCLResult:
    if conflict_limit < 1 or restart_interval < 1:
        raise ValueError("Limites CDCL devem ser positivos")
    original = normalize_cnf(clauses)
    database = list(original)
    variables = sorted({abs(literal) for clause in database for literal in clause})
    assignment: dict[int, bool] = {}
    level: dict[int, int] = {}
    reason: dict[int, int | None] = {}
    trail: list[int] = []
    boundaries = [0]
    activity = {variable: 0.0 for variable in variables}
    decisions = conflicts = learned = restarts = 0

    def literal_value(literal: int) -> bool | None:
        value = assignment.get(abs(literal))
        return None if value is None else value is (literal > 0)

    def assign(literal: int, why: int | None) -> bool:
        variable, value = abs(literal), literal > 0
        if variable in assignment:
            return assignment[variable] == value
        assignment[variable] = value
        level[variable] = len(boundaries) - 1
        reason[variable] = why
        trail.append(literal)
        return True

    def propagate() -> int | None:
        changed = True
        while changed:
            changed = False
            for index, clause in enumerate(database):
                values = [literal_value(literal) for literal in clause]
                if any(value is True for value in values):
                    continue
                undecided = [literal for literal, value in zip(clause, values) if value is None]
                if not undecided:
                    return index
                if len(undecided) == 1:
                    if not assign(undecided[0], index):
                        return index
                    changed = True
        return None

    def resolve(first: frozenset[int], second: frozenset[int], variable: int) -> frozenset[int]:
        return frozenset(literal for literal in first | second if abs(literal) != variable)

    def analyze(conflict_index: int) -> tuple[frozenset[int], int]:
        current_level = len(boundaries) - 1
        learned_clause = database[conflict_index]
        while sum(level.get(abs(literal), 0) == current_level for literal in learned_clause) > 1:
            pivot = next(abs(literal) for literal in reversed(trail)
                         if literal in learned_clause or -literal in learned_clause)
            reason_index = reason.get(pivot)
            if reason_index is None:
                # Multiple decision literals cannot occur at one level, but keep fail-closed.
                break
            learned_clause = resolve(learned_clause, database[reason_index], pivot)
        levels = sorted({level.get(abs(literal), 0) for literal in learned_clause})
        backjump = levels[-2] if len(levels) > 1 else 0
        return learned_clause, backjump

    def backtrack(target: int) -> None:
        while len(boundaries) - 1 > target:
            start = boundaries.pop()
            for literal in trail[start:]:
                variable = abs(literal)
                assignment.pop(variable, None)
                level.pop(variable, None)
                reason.pop(variable, None)
            del trail[start:]

    while True:
        conflict = propagate()
        if conflict is not None:
            conflicts += 1
            if conflicts > conflict_limit:
                raise RuntimeError("CDCL excedeu conflict_limit")
            if len(boundaries) == 1:
                return CDCLResult(False, (), decisions, conflicts, learned, restarts)
            learned_clause, backjump = analyze(conflict)
            if not learned_clause:
                return CDCLResult(False, (), decisions, conflicts, learned, restarts)
            for literal in learned_clause:
                activity[abs(literal)] += 1.0
            database.append(learned_clause)
            learned += 1
            backtrack(backjump)
            undecided = [literal for literal in learned_clause if literal_value(literal) is None]
            if len(undecided) == 1:
                assign(undecided[0], len(database) - 1)
            if conflicts % restart_interval == 0:
                backtrack(0)
                restarts += 1
            continue
        if len(assignment) == len(variables):
            if not verify_assignment(original, assignment):
                raise ArithmeticError("Modelo CDCL falhou na verificação")
            return CDCLResult(True, tuple(sorted(assignment.items())), decisions,
                              conflicts, learned, restarts)
        variable = max((item for item in variables if item not in assignment),
                       key=lambda item: (activity[item], -item))
        boundaries.append(len(trail))
        decisions += 1
        assign(variable, None)


__all__ = ["CDCLResult", "solve_cdcl"]
