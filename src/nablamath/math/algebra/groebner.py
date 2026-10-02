"""Exact sparse multivariate polynomials and bounded Gröbner bases.

Buchberger's algorithm here targets small, auditable systems. Pair and reduction
budgets are explicit, and every algebraic decision uses exact rational arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable, Literal, Mapping, Sequence

from ...expression import Binary, Expr, Number, Symbol

Monomial = tuple[int, ...]
MonomialOrder = Literal["lex", "grlex", "grevlex"]


def _validate_monomial(monomial: Monomial, dimensions: int) -> None:
    if len(monomial) != dimensions or any(type(value) is not int or value < 0 for value in monomial):
        raise ValueError("Monômio deve ter um expoente inteiro não negativo por variável")


def _monomial_key(monomial: Monomial, order: MonomialOrder) -> tuple[int, ...]:
    if order == "lex":
        return monomial
    if order == "grlex":
        return (sum(monomial), *monomial)
    if order == "grevlex":
        return (sum(monomial), *(-exponent for exponent in reversed(monomial)))
    raise ValueError(f"Ordem monomial desconhecida: {order}")


def _divides(divisor: Monomial, dividend: Monomial) -> bool:
    return all(left <= right for left, right in zip(divisor, dividend))


def _quotient(dividend: Monomial, divisor: Monomial) -> Monomial:
    if not _divides(divisor, dividend):
        raise ValueError("Monômio não é divisível pelo divisor informado")
    return tuple(left - right for left, right in zip(dividend, divisor))


def _lcm(first: Monomial, second: Monomial) -> Monomial:
    return tuple(max(left, right) for left, right in zip(first, second))


@dataclass(frozen=True, init=False)
class Polynomial:
    """Canonical sparse polynomial over the rationals."""

    variables: tuple[str, ...]
    terms: tuple[tuple[Monomial, Fraction], ...]

    def __init__(
        self,
        variables: Sequence[str],
        terms: Mapping[Monomial, Fraction | int] | Iterable[tuple[Monomial, Fraction | int]],
    ) -> None:
        names = tuple(variables)
        if not names or len(set(names)) != len(names) or any(not name.isidentifier() for name in names):
            raise ValueError("Variáveis devem ser identificadores únicos")
        source = terms.items() if isinstance(terms, Mapping) else terms
        combined: dict[Monomial, Fraction] = {}
        for monomial, coefficient in source:
            monomial = tuple(monomial)
            _validate_monomial(monomial, len(names))
            value = Fraction(coefficient)
            combined[monomial] = combined.get(monomial, Fraction(0)) + value
        canonical = tuple(sorted((m, c) for m, c in combined.items() if c))
        object.__setattr__(self, "variables", names)
        object.__setattr__(self, "terms", canonical)

    @classmethod
    def zero(cls, variables: Sequence[str]) -> Polynomial:
        return cls(variables, {})

    @classmethod
    def constant(cls, variables: Sequence[str], value: Fraction | int) -> Polynomial:
        names = tuple(variables)
        return cls(names, {(0,) * len(names): value})

    @classmethod
    def generator(cls, variables: Sequence[str], name: str) -> Polynomial:
        names = tuple(variables)
        if name not in names:
            raise ValueError(f"Variável desconhecida: {name}")
        powers = tuple(1 if variable == name else 0 for variable in names)
        return cls(names, {powers: 1})

    @property
    def is_zero(self) -> bool:
        return not self.terms

    def _coerce(self, other: Polynomial | Fraction | int) -> Polynomial:
        if isinstance(other, Polynomial):
            if self.variables != other.variables:
                raise ValueError("Polinômios usam anéis de variáveis diferentes")
            return other
        return Polynomial.constant(self.variables, other)

    def __add__(self, other: Polynomial | Fraction | int) -> Polynomial:
        right = self._coerce(other)
        return Polynomial(self.variables, (*self.terms, *right.terms))

    __radd__ = __add__

    def __neg__(self) -> Polynomial:
        return Polynomial(self.variables, ((monomial, -coefficient) for monomial, coefficient in self.terms))

    def __sub__(self, other: Polynomial | Fraction | int) -> Polynomial:
        return self + -self._coerce(other)

    def __rsub__(self, other: Polynomial | Fraction | int) -> Polynomial:
        return self._coerce(other) - self

    def __mul__(self, other: Polynomial | Fraction | int) -> Polynomial:
        right = self._coerce(other)
        products = []
        for left_monomial, left_coefficient in self.terms:
            for right_monomial, right_coefficient in right.terms:
                products.append((tuple(a + b for a, b in zip(left_monomial, right_monomial)),
                                 left_coefficient * right_coefficient))
        return Polynomial(self.variables, products)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> Polynomial:
        if type(exponent) is not int or exponent < 0:
            raise ValueError("Expoente polinomial deve ser inteiro não negativo")
        result = Polynomial.constant(self.variables, 1)
        factor, power = self, exponent
        while power:
            if power & 1:
                result = result * factor
            factor = factor * factor
            power //= 2
        return result

    def leading_term(self, order: MonomialOrder = "grevlex") -> tuple[Monomial, Fraction]:
        if self.is_zero:
            raise ValueError("Polinômio zero não possui termo líder")
        return max(self.terms, key=lambda term: _monomial_key(term[0], order))

    def monic(self, order: MonomialOrder = "grevlex") -> Polynomial:
        if self.is_zero:
            return self
        coefficient = self.leading_term(order)[1]
        return Polynomial(self.variables, ((monomial, value / coefficient) for monomial, value in self.terms))

    def multiply_term(self, monomial: Monomial, coefficient: Fraction | int = 1) -> Polynomial:
        _validate_monomial(monomial, len(self.variables))
        scale = Fraction(coefficient)
        return Polynomial(self.variables, ((tuple(a + b for a, b in zip(existing, monomial)), value * scale)
                                            for existing, value in self.terms))

    def evaluate(self, values: Mapping[str, Fraction | int]) -> Fraction:
        missing = set(self.variables) - set(values)
        if missing:
            raise ValueError(f"Faltam valores para: {', '.join(sorted(missing))}")
        total = Fraction(0)
        for monomial, coefficient in self.terms:
            term = coefficient
            for name, exponent in zip(self.variables, monomial):
                term *= Fraction(values[name]) ** exponent
            total += term
        return total

    def to_expr(self) -> Expr:
        result: Expr = Number(Fraction(0))
        for monomial, coefficient in self.terms:
            term: Expr = Number(coefficient)
            for name, exponent in zip(self.variables, monomial):
                if exponent:
                    factor: Expr = Symbol(name)
                    if exponent != 1:
                        factor = Binary("**", factor, Number(Fraction(exponent)))
                    term = Binary("*", term, factor)
            result = Binary("+", result, term)
        return result


def polynomial_from_expr(expr: Expr, variables: Sequence[str]) -> Polynomial:
    """Convert the rational polynomial subset of the public expression AST."""
    names = tuple(variables)
    if isinstance(expr, Number):
        return Polynomial.constant(names, expr.value)
    if isinstance(expr, Symbol):
        return Polynomial.generator(names, expr.name)
    left = polynomial_from_expr(expr.left, names)
    if expr.op == "**":
        if not isinstance(expr.right, Number) or expr.right.value.denominator != 1:
            raise ValueError("Expoente polinomial deve ser inteiro literal")
        return left ** expr.right.value.numerator
    right = polynomial_from_expr(expr.right, names)
    if expr.op == "+":
        return left + right
    if expr.op == "-":
        return left - right
    if expr.op == "*":
        return left * right
    zero_monomial = (0,) * len(names)
    if expr.op == "/" and len(right.terms) == 1 and right.terms[0][0] == zero_monomial:
        denominator = right.terms[0][1]
        if denominator == 0:
            raise ZeroDivisionError("Divisão polinomial por zero")
        return left * (1 / denominator)
    raise ValueError(f"Operação {expr.op!r} não pertence ao anel polinomial")


def divide_polynomial(
    dividend: Polynomial,
    divisors: Sequence[Polynomial],
    *,
    order: MonomialOrder = "grevlex",
    step_limit: int = 100_000,
) -> tuple[tuple[Polynomial, ...], Polynomial]:
    """Multivariate division with a deterministic ordered divisor list."""
    if step_limit < 1:
        raise ValueError("step_limit deve ser positivo")
    if any(divisor.variables != dividend.variables for divisor in divisors):
        raise ValueError("Todos os divisores devem pertencer ao mesmo anel")
    if any(divisor.is_zero for divisor in divisors):
        raise ZeroDivisionError("Divisor polinomial zero")
    quotients = [Polynomial.zero(dividend.variables) for _ in divisors]
    remainder, current = Polynomial.zero(dividend.variables), dividend
    steps = 0
    while not current.is_zero:
        steps += 1
        if steps > step_limit:
            raise RuntimeError("Divisão polinomial excedeu o orçamento")
        current_monomial, current_coefficient = current.leading_term(order)
        reduced = False
        for index, divisor in enumerate(divisors):
            divisor_monomial, divisor_coefficient = divisor.leading_term(order)
            if _divides(divisor_monomial, current_monomial):
                monomial = _quotient(current_monomial, divisor_monomial)
                factor = Polynomial(dividend.variables, {monomial: current_coefficient / divisor_coefficient})
                quotients[index] = quotients[index] + factor
                current = current - factor * divisor
                reduced = True
                break
        if not reduced:
            leading = Polynomial(dividend.variables, {current_monomial: current_coefficient})
            remainder, current = remainder + leading, current - leading
    return tuple(quotients), remainder


def s_polynomial(first: Polynomial, second: Polynomial, order: MonomialOrder = "grevlex") -> Polynomial:
    if first.variables != second.variables:
        raise ValueError("Polinômios usam anéis diferentes")
    first_monomial, first_coefficient = first.leading_term(order)
    second_monomial, second_coefficient = second.leading_term(order)
    common = _lcm(first_monomial, second_monomial)
    left = first.multiply_term(_quotient(common, first_monomial), 1 / first_coefficient)
    right = second.multiply_term(_quotient(common, second_monomial), 1 / second_coefficient)
    return left - right


def groebner_basis(
    generators: Sequence[Polynomial],
    *,
    order: MonomialOrder = "grevlex",
    pair_limit: int = 10_000,
    division_step_limit: int = 100_000,
) -> tuple[Polynomial, ...]:
    """Compute a reduced monic Gröbner basis with explicit safety budgets."""
    if not generators:
        return ()
    if pair_limit < 1:
        raise ValueError("pair_limit deve ser positivo")
    variables = generators[0].variables
    if any(item.variables != variables for item in generators):
        raise ValueError("Geradores devem pertencer ao mesmo anel")
    basis: list[Polynomial] = []
    for generator in generators:
        if generator.is_zero:
            continue
        if basis:
            _, remainder = divide_polynomial(generator, basis, order=order,
                                             step_limit=division_step_limit)
        else:
            remainder = generator
        if not remainder.is_zero:
            basis.append(remainder.monic(order))
    pairs = list(combinations(range(len(basis)), 2))
    examined = cursor = 0
    while cursor < len(pairs):
        examined += 1
        if examined > pair_limit:
            raise RuntimeError("Buchberger excedeu o orçamento de pares")
        first_index, second_index = pairs[cursor]
        cursor += 1
        candidate = s_polynomial(basis[first_index], basis[second_index], order)
        _, remainder = divide_polynomial(candidate, basis, order=order,
                                         step_limit=division_step_limit)
        if not remainder.is_zero:
            new_index = len(basis)
            basis.append(remainder.monic(order))
            pairs.extend((index, new_index) for index in range(new_index))
    reduced: list[Polynomial] = []
    for index, polynomial in enumerate(basis):
        others = [item for other_index, item in enumerate(basis) if other_index != index]
        if others:
            _, remainder = divide_polynomial(polynomial, others, order=order,
                                             step_limit=division_step_limit)
        else:
            remainder = polynomial
        if not remainder.is_zero:
            monic = remainder.monic(order)
            if monic not in reduced:
                reduced.append(monic)
    return tuple(sorted(reduced, key=lambda item: _monomial_key(item.leading_term(order)[0], order)))


def is_in_ideal(polynomial: Polynomial, basis: Sequence[Polynomial], *,
                order: MonomialOrder = "grevlex") -> bool:
    if not basis:
        return polynomial.is_zero
    _, remainder = divide_polynomial(polynomial, basis, order=order)
    return remainder.is_zero


__all__ = ["Monomial", "MonomialOrder", "Polynomial", "divide_polynomial",
           "groebner_basis", "is_in_ideal", "polynomial_from_expr", "s_polynomial"]
