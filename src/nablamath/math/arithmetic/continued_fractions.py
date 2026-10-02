"""Frações contínuas simples finitas e aproximações racionais."""
from fractions import Fraction
from math import floor


def expand_rational(value: int | Fraction) -> tuple[int, ...]:
    value = Fraction(value); terms=[]
    while value.denominator != 1:
        integer = value.numerator // value.denominator
        terms.append(integer); value = 1 / (value - integer)
    terms.append(value.numerator)
    return tuple(terms)


def evaluate(terms: tuple[int, ...]) -> Fraction:
    if not terms or any(type(term) is not int for term in terms): raise ValueError("termos inteiros não vazios são obrigatórios")
    value = Fraction(terms[-1])
    for term in reversed(terms[:-1]):
        if value == 0: raise ZeroDivisionError("fração contínua inválida")
        value = term + 1 / value
    return value


def convergents(terms: tuple[int, ...]) -> tuple[Fraction, ...]:
    if not terms: raise ValueError("termos vazios")
    return tuple(evaluate(terms[:index]) for index in range(1, len(terms)+1))


def approximate_real(value: float, max_terms: int = 32, tolerance: float = 1e-12) -> tuple[int, ...]:
    if not 1 <= max_terms <= 10_000 or tolerance <= 0: raise ValueError("limites inválidos")
    terms=[]; current=value
    for _ in range(max_terms):
        integer=floor(current); terms.append(integer)
        remainder=current-integer
        if abs(remainder) <= tolerance: break
        current=1/remainder
    return tuple(terms)

__all__=["approximate_real","convergents","evaluate","expand_rational"]
