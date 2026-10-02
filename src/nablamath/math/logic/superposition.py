"""Bounded first-order resolution and equality superposition.

The calculus works on already-clausified formulas.  It supplies occurs-check
unification, standardization apart, binary resolution, equality factoring by
orientation, paramodulation into non-variable subterms, and replayable steps.
It is a small complete-calculus reference, not an industrial saturation prover.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Mapping


@dataclass(frozen=True, order=True)
class FOTerm:
    symbol: str
    arguments: tuple["FOTerm", ...] = ()
    variable: bool = False

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("Símbolo vazio")
        if self.variable and self.arguments:
            raise ValueError("Variáveis não possuem argumentos")


@dataclass(frozen=True, order=True)
class Atom:
    predicate: str
    arguments: tuple[FOTerm, ...]

    def __post_init__(self) -> None:
        if not self.predicate:
            raise ValueError("Predicado vazio")
        if self.predicate == "=" and len(self.arguments) != 2:
            raise ValueError("Igualdade deve ser binária")


@dataclass(frozen=True, order=True)
class FOLiteral:
    atom: Atom
    positive: bool = True


FOClause = frozenset[FOLiteral]
Substitution = dict[str, FOTerm]


@dataclass(frozen=True)
class SuperpositionStep:
    clause: FOClause
    rule: str
    left: int | None = None
    right: int | None = None


@dataclass(frozen=True)
class SuperpositionProof:
    refuted: bool
    input_count: int
    steps: tuple[SuperpositionStep, ...]


def variable(name: str) -> FOTerm:
    return FOTerm(name, variable=True)


def function(name: str, *arguments: FOTerm) -> FOTerm:
    return FOTerm(name, tuple(arguments))


def _walk(term: FOTerm, substitution: Mapping[str, FOTerm]) -> FOTerm:
    while term.variable and term.symbol in substitution:
        term = substitution[term.symbol]
    return term


def _occurs(name: str, term: FOTerm, substitution: Mapping[str, FOTerm]) -> bool:
    term = _walk(term, substitution)
    return (term.variable and term.symbol == name) or any(
        _occurs(name, argument, substitution) for argument in term.arguments
    )


def unify(left: FOTerm, right: FOTerm,
          substitution: Mapping[str, FOTerm] | None = None) -> Substitution | None:
    """Return a most-general unifier, rejecting cyclic substitutions."""
    result = dict(substitution or {})
    pending = [(left, right)]
    while pending:
        first, second = (_walk(item, result) for item in pending.pop())
        if first == second:
            continue
        if first.variable:
            if _occurs(first.symbol, second, result):
                return None
            result[first.symbol] = second
        elif second.variable:
            if _occurs(second.symbol, first, result):
                return None
            result[second.symbol] = first
        elif first.symbol != second.symbol or len(first.arguments) != len(second.arguments):
            return None
        else:
            pending.extend(zip(first.arguments, second.arguments))
    return result


def substitute_term(term: FOTerm, substitution: Mapping[str, FOTerm]) -> FOTerm:
    walked = _walk(term, substitution)
    if walked.variable:
        return walked
    return FOTerm(walked.symbol, tuple(substitute_term(arg, substitution)
                                       for arg in walked.arguments))


def _substitute_literal(literal: FOLiteral, substitution: Mapping[str, FOTerm]) -> FOLiteral:
    return FOLiteral(Atom(literal.atom.predicate,
                          tuple(substitute_term(arg, substitution)
                                for arg in literal.atom.arguments)), literal.positive)


def _normalize(clause: Iterable[FOLiteral], substitution: Mapping[str, FOTerm]) -> FOClause | None:
    result = frozenset(_substitute_literal(literal, substitution) for literal in clause)
    if any(FOLiteral(literal.atom, not literal.positive) in result for literal in result):
        return None
    return _canonical_clause(result)


def _variable_names(term: FOTerm) -> set[str]:
    if term.variable:
        return {term.symbol}
    return set().union(*(_variable_names(argument) for argument in term.arguments), set())


def _canonical_clause(clause: FOClause) -> FOClause:
    names = sorted({name for literal in clause for argument in literal.atom.arguments
                    for name in _variable_names(argument)})
    substitution = {name: variable(f"V{index}") for index, name in enumerate(names)}
    return frozenset(_substitute_literal(literal, substitution) for literal in clause)


def _rename_term(term: FOTerm, prefix: str) -> FOTerm:
    if term.variable:
        return variable(prefix + term.symbol)
    return FOTerm(term.symbol, tuple(_rename_term(arg, prefix) for arg in term.arguments))


def _rename_clause(clause: FOClause, prefix: str) -> FOClause:
    return frozenset(FOLiteral(Atom(literal.atom.predicate,
                                    tuple(_rename_term(arg, prefix)
                                          for arg in literal.atom.arguments)),
                               literal.positive) for literal in clause)


def _term_positions(term: FOTerm, position: tuple[int, ...] = ()) -> Iterator[tuple[tuple[int, ...], FOTerm]]:
    if not term.variable:
        yield position, term
    for index, argument in enumerate(term.arguments):
        yield from _term_positions(argument, position + (index,))


def _replace(term: FOTerm, position: tuple[int, ...], replacement: FOTerm) -> FOTerm:
    if not position:
        return replacement
    index, *tail = position
    arguments = list(term.arguments)
    arguments[index] = _replace(arguments[index], tuple(tail), replacement)
    return FOTerm(term.symbol, tuple(arguments), term.variable)


def _literal_with_replacement(literal: FOLiteral, argument: int,
                              position: tuple[int, ...], replacement: FOTerm) -> FOLiteral:
    arguments = list(literal.atom.arguments)
    arguments[argument] = _replace(arguments[argument], position, replacement)
    return FOLiteral(Atom(literal.atom.predicate, tuple(arguments)), literal.positive)


def infer(left: FOClause, right: FOClause, *, tag: str = "p") -> set[tuple[str, FOClause]]:
    """Enumerate binary resolution and superposition conclusions for two clauses."""
    first, second = _rename_clause(left, tag + "l_"), _rename_clause(right, tag + "r_")
    conclusions: set[tuple[str, FOClause]] = set()
    for left_literal in first:
        for right_literal in second:
            if (left_literal.positive != right_literal.positive
                    and left_literal.atom.predicate == right_literal.atom.predicate
                    and len(left_literal.atom.arguments) == len(right_literal.atom.arguments)):
                substitution: Substitution | None = {}
                for one, two in zip(left_literal.atom.arguments, right_literal.atom.arguments):
                    if substitution is not None:
                        substitution = unify(one, two, substitution)
                if substitution is not None:
                    result = _normalize((first - {left_literal}) | (second - {right_literal}),
                                        substitution)
                    if result is not None:
                        conclusions.add(("resolution", result))
    for source, target in ((first, second), (second, first)):
        for equality in source:
            if not equality.positive or equality.atom.predicate != "=":
                continue
            for lhs, rhs in (equality.atom.arguments, tuple(reversed(equality.atom.arguments))):
                if lhs.variable:
                    continue
                for literal in target:
                    for argument_index, argument in enumerate(literal.atom.arguments):
                        for position, subterm in _term_positions(argument):
                            substitution = unify(lhs, subterm)
                            if substitution is None:
                                continue
                            replaced = _literal_with_replacement(literal, argument_index,
                                                                 position, rhs)
                            result = _normalize((source - {equality}) | (target - {literal})
                                                | {replaced}, substitution)
                            if result is not None:
                                conclusions.add(("superposition", result))
    return conclusions


def superposition_refutation(clauses: Iterable[Iterable[FOLiteral]], *,
                              step_limit: int = 10_000) -> SuperpositionProof:
    """Saturate a finite clause set until a refutation or fixed point is reached."""
    if step_limit < 1:
        raise ValueError("step_limit deve ser positivo")
    steps = [SuperpositionStep(_canonical_clause(frozenset(clause)), "input")
             for clause in clauses]
    known = {step.clause for step in steps}
    if frozenset() in known:
        return SuperpositionProof(True, len(steps), tuple(steps))
    input_count = len(steps)
    cursor = 0
    pairs = [(left, right) for left in range(len(steps))
             for right in range(left, len(steps))]
    while cursor < len(pairs):
        left, right = pairs[cursor]
        cursor += 1
        for rule, clause in sorted(infer(steps[left].clause, steps[right].clause,
                                                tag=f"s{cursor}_"),
                                   key=lambda item: (item[0], repr(item[1]))):
            if clause in known:
                continue
            if len(steps) >= step_limit:
                raise RuntimeError("Superposição excedeu step_limit")
            index = len(steps)
            steps.append(SuperpositionStep(clause, rule, left, right))
            known.add(clause)
            if not clause:
                proof = SuperpositionProof(True, input_count, tuple(steps))
                if not verify_superposition(proof):
                    raise ArithmeticError("Prova interna de superposição inválida")
                return proof
            pairs.extend((previous, index) for previous in range(index + 1))
    return SuperpositionProof(False, input_count, tuple(steps))


def verify_superposition(proof: SuperpositionProof) -> bool:
    """Replay every derived clause from its two recorded parents."""
    if not 0 <= proof.input_count <= len(proof.steps):
        return False
    for index, step in enumerate(proof.steps):
        if index < proof.input_count:
            if step.rule != "input" or step.left is not None or step.right is not None:
                return False
            continue
        if step.rule not in {"resolution", "superposition"}:
            return False
        if step.left is None or step.right is None:
            return False
        if not 0 <= step.left < index or not 0 <= step.right < index:
            return False
        possible = infer(proof.steps[step.left].clause, proof.steps[step.right].clause,
                         tag=f"verify{index}_")
        if (step.rule, step.clause) not in possible:
            return False
    return proof.refuted is bool(proof.steps and not proof.steps[-1].clause)


__all__ = ["Atom", "FOClause", "FOLiteral", "FOTerm", "SuperpositionProof",
           "SuperpositionStep", "function", "infer", "substitute_term",
           "superposition_refutation", "unify", "variable", "verify_superposition"]
