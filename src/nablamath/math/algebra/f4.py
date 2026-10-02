"""Exact F4-style Gröbner basis computation over the rationals.

The implementation performs degree-batched critical-pair selection, symbolic
preprocessing into Macaulay matrices, exact Gaussian elimination and extraction
of new reducers.  It is a reference implementation, not the F4 paper's optimized
sparse data structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Literal, Sequence

from .groebner import Monomial, MonomialOrder, Polynomial, divide_polynomial


def _key(monomial: Monomial, order: MonomialOrder) -> tuple[int, ...]:
    if order == "lex":
        return monomial
    if order == "grlex":
        return (sum(monomial), *monomial)
    return (sum(monomial), *(-value for value in reversed(monomial)))


def _divides(left: Monomial, right: Monomial) -> bool:
    return all(first <= second for first, second in zip(left, right))


def _quotient(left: Monomial, right: Monomial) -> Monomial:
    return tuple(first - second for first, second in zip(left, right))


def _lcm(left: Monomial, right: Monomial) -> Monomial:
    return tuple(max(first, second) for first, second in zip(left, right))


def _s_polynomial(first: Polynomial, second: Polynomial,
                  order: MonomialOrder) -> Polynomial:
    left_monomial, left_coefficient = first.leading_term(order)
    right_monomial, right_coefficient = second.leading_term(order)
    common = _lcm(left_monomial, right_monomial)
    return (first.multiply_term(_quotient(common, left_monomial), 1 / left_coefficient)
            - second.multiply_term(_quotient(common, right_monomial), 1 / right_coefficient))


def _rref(matrix: list[list[Fraction]]) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    if not matrix:
        return [], ()
    pivot_row, pivots = 0, []
    for column in range(len(matrix[0])):
        candidate = next((row for row in range(pivot_row, len(matrix))
                          if matrix[row][column]), None)
        if candidate is None:
            continue
        matrix[pivot_row], matrix[candidate] = matrix[candidate], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row != pivot_row and matrix[row][column]:
                factor = matrix[row][column]
                matrix[row] = [value - factor * pivot
                               for value, pivot in zip(matrix[row], matrix[pivot_row])]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return matrix, tuple(pivots)


@dataclass(frozen=True)
class MacaulayMatrix:
    monomials: tuple[Monomial, ...]
    rows: tuple[tuple[Fraction, ...], ...]
    source_rows: int


@dataclass(frozen=True)
class F4Result:
    basis: tuple[Polynomial, ...]
    pair_batches: int
    matrices: int
    maximum_rows: int
    maximum_columns: int
    maximum_nonzeros: int


def _sparse_rref(rows: Sequence[Sequence[Fraction]]) -> tuple[list[dict[int, Fraction]], tuple[int, ...]]:
    """Exact sparse Gauss–Jordan elimination without materializing fill-in zeros."""
    sparse = [{column: value for column, value in enumerate(row) if value}
              for row in rows]
    pivots: list[int] = []
    pivot_row = 0
    columns = max((max(row, default=-1) for row in sparse), default=-1) + 1
    for column in range(columns):
        candidate = next((index for index in range(pivot_row, len(sparse))
                          if sparse[index].get(column)), None)
        if candidate is None:
            continue
        sparse[pivot_row], sparse[candidate] = sparse[candidate], sparse[pivot_row]
        scale = sparse[pivot_row][column]
        sparse[pivot_row] = {key: value / scale for key, value in sparse[pivot_row].items()}
        pivot = sparse[pivot_row]
        for index, row in enumerate(sparse):
            if index == pivot_row or not row.get(column):
                continue
            factor = row[column]
            keys = set(row) | set(pivot)
            reduced = {key: row.get(key, Fraction(0)) - factor * pivot.get(key, Fraction(0))
                       for key in keys}
            sparse[index] = {key: value for key, value in reduced.items() if value}
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(sparse):
            break
    return sparse, tuple(pivots)


def build_macaulay_matrix(sources: Sequence[Polynomial], basis: Sequence[Polynomial], *,
                          order: MonomialOrder = "grevlex",
                          row_limit: int = 100_000,
                          column_limit: int = 100_000) -> MacaulayMatrix:
    """Perform F4 symbolic preprocessing and build an exact sparse-to-dense matrix."""
    if not sources:
        return MacaulayMatrix((), (), 0)
    variables = sources[0].variables
    if any(polynomial.variables != variables for polynomial in (*sources, *basis)):
        raise ValueError("Polinômios pertencem a anéis diferentes")
    rows = list(sources)
    seen_rows = set(rows)
    processed_monomials: set[Monomial] = set()
    cursor = 0
    while cursor < len(rows):
        polynomial = rows[cursor]
        cursor += 1
        for monomial, _ in polynomial.terms:
            if monomial in processed_monomials:
                continue
            processed_monomials.add(monomial)
            reducer = next((candidate for candidate in basis
                            if _divides(candidate.leading_term(order)[0], monomial)), None)
            if reducer is None:
                continue
            leading, coefficient = reducer.leading_term(order)
            multiple = reducer.multiply_term(_quotient(monomial, leading), 1 / coefficient)
            if multiple not in seen_rows:
                if len(rows) >= row_limit:
                    raise RuntimeError("Pré-processamento F4 excedeu row_limit")
                rows.append(multiple)
                seen_rows.add(multiple)
    monomials = tuple(sorted({monomial for row in rows for monomial, _ in row.terms},
                             key=lambda item: _key(item, order), reverse=True))
    if len(monomials) > column_limit:
        raise RuntimeError("Matriz Macaulay excedeu column_limit")
    index = {monomial: column for column, monomial in enumerate(monomials)}
    dense = []
    for polynomial in rows:
        row = [Fraction(0)] * len(monomials)
        for monomial, coefficient in polynomial.terms:
            row[index[monomial]] = coefficient
        dense.append(tuple(row))
    return MacaulayMatrix(monomials, tuple(dense), len(sources))


def f4_basis(generators: Sequence[Polynomial], *, order: MonomialOrder = "grevlex",
             pair_limit: int = 100_000, row_limit: int = 100_000,
             column_limit: int = 100_000) -> F4Result:
    """Compute a Gröbner basis using F4 matrix batches and exact verification."""
    if not generators:
        return F4Result((), 0, 0, 0, 0, 0)
    variables = generators[0].variables
    if any(item.variables != variables for item in generators):
        raise ValueError("Geradores pertencem a anéis diferentes")
    basis: list[Polynomial] = []
    for generator in generators:
        if generator.is_zero:
            continue
        _, remainder = divide_polynomial(generator, basis, order=order) if basis else ((), generator)
        if not remainder.is_zero:
            basis.append(remainder.monic(order))
    pairs = list(combinations(range(len(basis)), 2))
    processed: set[tuple[int, int]] = set()
    batches = matrices = maximum_rows = maximum_columns = maximum_nonzeros = 0
    while True:
        pending = [pair for pair in pairs if pair not in processed]
        if not pending:
            break
        if len(processed) + len(pending) > pair_limit:
            raise RuntimeError("F4 excedeu pair_limit")
        degrees = {pair: sum(_lcm(basis[pair[0]].leading_term(order)[0],
                                  basis[pair[1]].leading_term(order)[0])) for pair in pending}
        minimum_degree = min(degrees.values())
        batch = [pair for pair in pending if degrees[pair] == minimum_degree]
        processed.update(batch)
        sources = [_s_polynomial(basis[left], basis[right], order) for left, right in batch]
        sources = [source for source in sources if not source.is_zero]
        batches += 1
        if not sources:
            continue
        macaulay = build_macaulay_matrix(sources, basis, order=order,
                                         row_limit=row_limit, column_limit=column_limit)
        reduced, _ = _sparse_rref(macaulay.rows)
        matrices += 1
        maximum_rows, maximum_columns = max(maximum_rows, len(reduced)), \
            max(maximum_columns, len(macaulay.monomials))
        maximum_nonzeros = max(maximum_nonzeros,
                               sum(len(row) for row in reduced))
        additions: list[Polynomial] = []
        for row in reduced:
            polynomial = Polynomial(variables, ((macaulay.monomials[column], coefficient)
                                                 for column, coefficient in row.items()))
            if polynomial.is_zero:
                continue
            _, remainder = divide_polynomial(polynomial, (*basis, *additions), order=order)
            if not remainder.is_zero:
                monic = remainder.monic(order)
                if monic not in basis and monic not in additions:
                    additions.append(monic)
        for polynomial in additions:
            new_index = len(basis)
            basis.append(polynomial)
            pairs.extend((index, new_index) for index in range(new_index))
    # Every critical S-polynomial is checked as a postcondition.
    for left, right in combinations(basis, 2):
        _, remainder = divide_polynomial(_s_polynomial(left, right, order), basis, order=order)
        if not remainder.is_zero:
            raise ArithmeticError("Pós-condição de Buchberger falhou após F4")
    return F4Result(tuple(basis), batches, matrices, maximum_rows, maximum_columns,
                    maximum_nonzeros)


__all__ = ["F4Result", "MacaulayMatrix", "build_macaulay_matrix", "f4_basis"]
