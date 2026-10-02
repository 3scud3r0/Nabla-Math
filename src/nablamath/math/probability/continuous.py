"""Validated continuous distributions with analytic moments and CDFs."""

from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class NormalDistribution:
    mean: float = 0.0
    standard_deviation: float = 1.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.mean) or not math.isfinite(self.standard_deviation) or self.standard_deviation <= 0:
            raise ValueError("Parâmetros normais inválidos")

    @property
    def variance(self) -> float:
        return self.standard_deviation**2

    def pdf(self, value: float) -> float:
        z = (value - self.mean) / self.standard_deviation
        return math.exp(-z * z / 2) / (self.standard_deviation * math.sqrt(2 * math.pi))

    def cdf(self, value: float) -> float:
        return .5 * (1 + math.erf((value - self.mean) / (self.standard_deviation * math.sqrt(2))))

    def quantile(self, probability: float, *, tolerance: float = 1e-12) -> float:
        if not 0 < probability < 1:
            raise ValueError("Probabilidade deve estar em (0,1)")
        low, high = self.mean - 12 * self.standard_deviation, self.mean + 12 * self.standard_deviation
        while high - low > tolerance * self.standard_deviation:
            middle = (low + high) / 2
            if self.cdf(middle) < probability:
                low = middle
            else:
                high = middle
        return (low + high) / 2


@dataclass(frozen=True)
class ExponentialDistribution:
    rate: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.rate) or self.rate <= 0:
            raise ValueError("Taxa deve ser finita e positiva")

    @property
    def mean(self) -> float:
        return 1 / self.rate

    @property
    def variance(self) -> float:
        return 1 / self.rate**2

    def pdf(self, value: float) -> float:
        return self.rate * math.exp(-self.rate * value) if value >= 0 else 0.0

    def cdf(self, value: float) -> float:
        return -math.expm1(-self.rate * value) if value >= 0 else 0.0

    def quantile(self, probability: float) -> float:
        if not 0 <= probability < 1:
            raise ValueError("Probabilidade deve estar em [0,1)")
        return -math.log1p(-probability) / self.rate


@dataclass(frozen=True)
class PoissonDistribution:
    rate: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.rate) or self.rate <= 0:
            raise ValueError("Taxa deve ser finita e positiva")

    def pmf(self, value: int) -> float:
        if type(value) is not int:
            raise ValueError("Poisson usa contagens inteiras")
        return math.exp(-self.rate + value * math.log(self.rate) - math.lgamma(value + 1)) if value >= 0 else 0.0

    def cdf(self, value: int) -> float:
        if type(value) is not int:
            raise ValueError("Poisson usa contagens inteiras")
        return math.fsum(self.pmf(index) for index in range(max(-1, value) + 1))


__all__ = ["ExponentialDistribution", "NormalDistribution", "PoissonDistribution"]
