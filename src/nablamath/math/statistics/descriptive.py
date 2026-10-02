"""Estatística descritiva exata para amostras racionais finitas."""

from fractions import Fraction
from typing import Iterable


def _sample(values: Iterable[int | Fraction]) -> tuple[Fraction, ...]:
    result = tuple(Fraction(value) for value in values)
    if not result: raise ValueError("amostra vazia")
    return result


def mean(values: Iterable[int | Fraction]) -> Fraction:
    data = _sample(values)
    return sum(data, Fraction()) / len(data)


def variance(values: Iterable[int | Fraction], *, sample: bool = False) -> Fraction:
    data = _sample(values)
    if sample and len(data) < 2: raise ValueError("variância amostral requer dois valores")
    center = sum(data, Fraction()) / len(data)
    return sum(((value - center) ** 2 for value in data), Fraction()) / (len(data) - int(sample))


def covariance(left: Iterable[int | Fraction], right: Iterable[int | Fraction], *, sample: bool = False) -> Fraction:
    x, y = _sample(left), _sample(right)
    if len(x) != len(y): raise ValueError("amostras precisam ter o mesmo tamanho")
    if sample and len(x) < 2: raise ValueError("covariância amostral requer dois pares")
    mx, my = mean(x), mean(y)
    return sum(((a - mx) * (b - my) for a, b in zip(x, y, strict=True)), Fraction()) / (len(x) - int(sample))


__all__ = ["covariance", "mean", "variance"]
