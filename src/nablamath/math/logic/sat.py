"""Bounded DPLL SAT solver with independently checkable assignments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

Literal = int
Clause = frozenset[Literal]
CNF = tuple[Clause, ...]


@dataclass(frozen=True)
class SATResult:
    satisfiable: bool
    assignment: tuple[tuple[int, bool], ...]
    decisions: int
    propagations: int


def normalize_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    normalized: list[Clause] = []
    for raw_clause in clauses:
        clause = frozenset(raw_clause)
        if any(type(literal) is not int or literal == 0 for literal in clause):
            raise ValueError("Literais devem ser inteiros não nulos")
        if any(-literal in clause for literal in clause):
            continue  # tautological clause
        normalized.append(clause)
    return tuple(dict.fromkeys(normalized))


def verify_assignment(cnf: CNF, assignment: Mapping[int, bool]) -> bool:
    return all(any(assignment.get(abs(literal)) is (literal > 0) for literal in clause)
               for clause in cnf)


def solve_sat(clauses: Iterable[Iterable[int]], *, decision_limit: int = 1_000_000) -> SATResult:
    """Solve CNF using unit propagation, pure literals and deterministic DPLL."""
    if decision_limit < 1:
        raise ValueError("decision_limit deve ser positivo")
    cnf = normalize_cnf(clauses)
    decisions = propagations = 0

    def simplify(formula: CNF, variable: int, value: bool) -> CNF | None:
        nonlocal propagations
        true_literal = variable if value else -variable
        false_literal = -true_literal
        result = []
        for clause in formula:
            if true_literal in clause:
                continue
            reduced = clause - {false_literal}
            if not reduced:
                return None
            if len(reduced) < len(clause):
                propagations += 1
            result.append(reduced)
        return tuple(result)

    def search(formula: CNF, assignment: dict[int, bool]) -> dict[int, bool] | None:
        nonlocal decisions, propagations
        while True:
            if not formula:
                return assignment
            if any(not clause for clause in formula):
                return None
            units = sorted((next(iter(clause)) for clause in formula if len(clause) == 1),
                           key=lambda literal: (abs(literal), literal < 0))
            if units:
                literal = units[0]
                variable, value = abs(literal), literal > 0
                if variable in assignment and assignment[variable] != value:
                    return None
                assignment = {**assignment, variable: value}
                formula = simplify(formula, variable, value)
                propagations += 1
                if formula is None:
                    return None
                continue
            all_literals = set().union(*formula)
            pure = sorted((literal for literal in all_literals if -literal not in all_literals),
                          key=lambda literal: (abs(literal), literal < 0))
            if pure:
                literal = pure[0]
                variable, value = abs(literal), literal > 0
                assignment = {**assignment, variable: value}
                formula = simplify(formula, variable, value)
                propagations += 1
                if formula is None:
                    return None
                continue
            break
        decisions += 1
        if decisions > decision_limit:
            raise RuntimeError("DPLL excedeu o orçamento de decisões")
        variable = min(abs(literal) for clause in formula for literal in clause
                       if abs(literal) not in assignment)
        for value in (True, False):
            reduced = simplify(formula, variable, value)
            if reduced is not None:
                solved = search(reduced, {**assignment, variable: value})
                if solved is not None:
                    return solved
        return None

    assignment = search(cnf, {})
    if assignment is None:
        return SATResult(False, (), decisions, propagations)
    variables = {abs(literal) for clause in cnf for literal in clause}
    complete = {variable: assignment.get(variable, False) for variable in variables}
    if not verify_assignment(cnf, complete):
        raise ArithmeticError("Certificado SAT interno inválido")
    return SATResult(True, tuple(sorted(complete.items())), decisions, propagations)


__all__ = ["CNF", "Clause", "Literal", "SATResult", "normalize_cnf", "solve_sat",
           "verify_assignment"]
