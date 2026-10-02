"""Signature-driven F5 reference algorithm with verified completion.

This implementation uses position-over-term signatures, signature-safe reduction,
rewritable/syzygy criteria and a final Buchberger audit.  Any pairs required by the
audit are completed rather than trusting an unsound criterion implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from .groebner import Monomial, MonomialOrder, Polynomial, divide_polynomial, s_polynomial


def _divides(left: Monomial, right: Monomial) -> bool:
    return all(first <= second for first, second in zip(left, right))


def _quotient(left: Monomial, right: Monomial) -> Monomial:
    return tuple(first - second for first, second in zip(left, right))


def _multiply(left: Monomial, right: Monomial) -> Monomial:
    return tuple(first + second for first, second in zip(left, right))


def _lcm(left: Monomial, right: Monomial) -> Monomial:
    return tuple(max(first, second) for first, second in zip(left, right))


def _monomial_key(value: Monomial, order: MonomialOrder) -> tuple[int, ...]:
    if order == "lex":
        return value
    if order == "grlex":
        return (sum(value), *value)
    return (sum(value), *(-item for item in reversed(value)))


@dataclass(frozen=True)
class Signature:
    generator: int
    monomial: Monomial


@dataclass(frozen=True)
class LabeledPolynomial:
    signature: Signature
    polynomial: Polynomial


@dataclass(frozen=True)
class F5Result:
    basis: tuple[Polynomial, ...]
    labeled_basis: tuple[LabeledPolynomial, ...]
    processed_pairs: int
    rejected_rewritable: int
    rejected_syzygy: int
    completion_pairs: int


def _signature_key(signature: Signature, order: MonomialOrder) -> tuple[object, ...]:
    return (signature.generator, *_monomial_key(signature.monomial, order))


def _scale_signature(signature: Signature, monomial: Monomial) -> Signature:
    return Signature(signature.generator, _multiply(signature.monomial, monomial))


def _maximum_signature(left: Signature, right: Signature,
                       order: MonomialOrder) -> Signature:
    return max((left, right), key=lambda item: _signature_key(item, order))


def _signature_safe_reduce(labeled: LabeledPolynomial,
                           basis: Sequence[LabeledPolynomial],
                           order: MonomialOrder) -> LabeledPolynomial:
    current = labeled.polynomial
    remainder = Polynomial.zero(current.variables)
    while not current.is_zero:
        leading, coefficient = current.leading_term(order)
        reducer = None
        for candidate in basis:
            candidate_leading, candidate_coefficient = candidate.polynomial.leading_term(order)
            if not _divides(candidate_leading, leading):
                continue
            multiplier = _quotient(leading, candidate_leading)
            scaled = _scale_signature(candidate.signature, multiplier)
            if _signature_key(scaled, order) < _signature_key(labeled.signature, order):
                reducer = candidate, multiplier, candidate_coefficient
                break
        if reducer is None:
            term = Polynomial(current.variables, {leading: coefficient})
            remainder, current = remainder + term, current - term
        else:
            candidate, multiplier, candidate_coefficient = reducer
            current = current - candidate.polynomial.multiply_term(
                multiplier, coefficient / candidate_coefficient
            )
    return LabeledPolynomial(labeled.signature, remainder)


def f5_basis(generators: Sequence[Polynomial], *, order: MonomialOrder = "grevlex",
             pair_limit: int = 100_000) -> F5Result:
    if not generators:
        return F5Result((), (), 0, 0, 0, 0)
    variables = generators[0].variables
    if any(item.variables != variables for item in generators):
        raise ValueError("Geradores pertencem a anéis diferentes")
    unit = (0,) * len(variables)
    labeled: list[LabeledPolynomial] = []
    known_signatures: list[Signature] = []
    leading_ideals: list[list[Monomial]] = [[] for _ in generators]
    for index, generator in enumerate(generators):
        if generator.is_zero:
            continue
        candidate = LabeledPolynomial(Signature(index, unit), generator.monic(order))
        reduced = _signature_safe_reduce(candidate, labeled, order)
        if not reduced.polynomial.is_zero:
            labeled.append(LabeledPolynomial(reduced.signature, reduced.polynomial.monic(order)))
            known_signatures.append(reduced.signature)
            leading_ideals[index].append(reduced.polynomial.leading_term(order)[0])
    pairs = list(combinations(range(len(labeled)), 2))
    cursor = processed = rewritable = syzygy = 0
    while cursor < len(pairs):
        if processed >= pair_limit:
            raise RuntimeError("F5 excedeu pair_limit")
        left_index, right_index = pairs[cursor]
        cursor += 1
        processed += 1
        left, right = labeled[left_index], labeled[right_index]
        left_leading = left.polynomial.leading_term(order)[0]
        right_leading = right.polynomial.leading_term(order)[0]
        common = _lcm(left_leading, right_leading)
        left_signature = _scale_signature(left.signature, _quotient(common, left_leading))
        right_signature = _scale_signature(right.signature, _quotient(common, right_leading))
        signature = _maximum_signature(left_signature, right_signature, order)
        if any(existing.generator == signature.generator
               and _divides(existing.monomial, signature.monomial)
               and existing != signature for existing in known_signatures):
            rewritable += 1
            continue
        if any(_divides(monomial, signature.monomial)
               for generator_index, ideal in enumerate(leading_ideals)
               if generator_index < signature.generator for monomial in ideal):
            syzygy += 1
            continue
        candidate = LabeledPolynomial(signature,
                                      s_polynomial(left.polynomial, right.polynomial, order))
        reduced = _signature_safe_reduce(candidate, labeled, order)
        known_signatures.append(signature)
        if reduced.polynomial.is_zero:
            continue
        polynomial = reduced.polynomial.monic(order)
        new_index = len(labeled)
        labeled.append(LabeledPolynomial(signature, polynomial))
        leading_ideals[signature.generator].append(polynomial.leading_term(order)[0])
        pairs.extend((index, new_index) for index in range(new_index))

    # Verified completion retains correctness even when a signature criterion is conservative.
    completion = 0
    basis = [item.polynomial for item in labeled]
    while True:
        addition = None
        for left, right in combinations(basis, 2):
            _, remainder = divide_polynomial(s_polynomial(left, right, order), basis, order=order)
            if not remainder.is_zero:
                addition = remainder.monic(order)
                break
        if addition is None:
            break
        completion += 1
        basis.append(addition)
        labeled.append(LabeledPolynomial(Signature(len(generators) - 1, unit), addition))
        if processed + completion > pair_limit:
            raise RuntimeError("Conclusão verificada de F5 excedeu pair_limit")
    return F5Result(tuple(basis), tuple(labeled), processed, rewritable, syzygy, completion)


__all__ = ["F5Result", "LabeledPolynomial", "Signature", "f5_basis"]
