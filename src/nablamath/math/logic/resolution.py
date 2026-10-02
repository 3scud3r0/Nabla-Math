"""Propositional resolution refutations with replayable proof steps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .sat import Clause, normalize_cnf


@dataclass(frozen=True)
class ResolutionStep:
    clause: Clause
    left: int | None
    right: int | None
    pivot: int | None


@dataclass(frozen=True)
class ResolutionProof:
    unsatisfiable: bool
    steps: tuple[ResolutionStep, ...]


def resolution_refutation(clauses: Iterable[Iterable[int]], *,
                          step_limit: int = 100_000) -> ResolutionProof:
    if step_limit < 1:
        raise ValueError("step_limit deve ser positivo")
    initial = normalize_cnf(clauses)
    steps = [ResolutionStep(clause, None, None, None) for clause in initial]
    index = {step.clause: position for position, step in enumerate(steps)}
    if frozenset() in index:
        return ResolutionProof(True, tuple(steps))
    cursor = 0
    pairs = [(left, right) for left in range(len(steps)) for right in range(left + 1, len(steps))]
    while cursor < len(pairs):
        left_index, right_index = pairs[cursor]
        cursor += 1
        left, right = steps[left_index].clause, steps[right_index].clause
        for pivot in sorted((literal for literal in left if -literal in right), key=abs):
            resolvent = frozenset((left - {pivot}) | (right - {-pivot}))
            if any(-literal in resolvent for literal in resolvent) or resolvent in index:
                continue
            if len(steps) >= step_limit:
                raise RuntimeError("Resolução excedeu o orçamento")
            new_index = len(steps)
            steps.append(ResolutionStep(resolvent, left_index, right_index, pivot))
            index[resolvent] = new_index
            if not resolvent:
                proof = ResolutionProof(True, tuple(steps))
                if not verify_resolution(initial, proof):
                    raise ArithmeticError("Prova de resolução interna inválida")
                return proof
            pairs.extend((previous, new_index) for previous in range(new_index))
    return ResolutionProof(False, tuple(steps))


def verify_resolution(initial: tuple[Clause, ...], proof: ResolutionProof) -> bool:
    if len(proof.steps) < len(initial):
        return False
    for index, clause in enumerate(initial):
        step = proof.steps[index]
        if step.clause != clause or any(value is not None for value in (step.left, step.right, step.pivot)):
            return False
    for index, step in enumerate(proof.steps[len(initial):], start=len(initial)):
        if step.left is None or step.right is None or step.pivot is None:
            return False
        if not 0 <= step.left < index or not 0 <= step.right < index:
            return False
        left, right = proof.steps[step.left].clause, proof.steps[step.right].clause
        if step.pivot not in left or -step.pivot not in right:
            return False
        if step.clause != frozenset((left - {step.pivot}) | (right - {-step.pivot})):
            return False
    return proof.unsatisfiable is bool(proof.steps and not proof.steps[-1].clause)


__all__ = ["ResolutionProof", "ResolutionStep", "resolution_refutation", "verify_resolution"]
