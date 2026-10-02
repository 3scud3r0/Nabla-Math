"""Estatística descritiva para séries temporais univariadas finitas."""

from __future__ import annotations

import math
from collections.abc import Iterable


def _series(values: Iterable[float], *, minimum: int = 1) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if len(result) < minimum:
        raise ValueError(f"série requer ao menos {minimum} observações")
    if len(result) > 10_000_000:
        raise ValueError("série excede o limite")
    if not all(math.isfinite(value) for value in result):
        raise ValueError("série contém valor não finito")
    return result


def differences(values: Iterable[float], order: int = 1) -> tuple[float, ...]:
    """Calcula diferenças sucessivas na ordem solicitada."""
    result = _series(values)
    if not isinstance(order, int) or not 0 <= order < len(result):
        raise ValueError("ordem inválida")
    for _ in range(order):
        result = tuple(right - left for left, right in zip(result, result[1:]))
    return result


def moving_average(values: Iterable[float], window: int) -> tuple[float, ...]:
    """Calcula médias móveis simples em tempo linear."""
    series = _series(values)
    if not isinstance(window, int) or not 1 <= window <= len(series):
        raise ValueError("janela inválida")
    total = sum(series[:window])
    result = [total / window]
    for index in range(window, len(series)):
        total += series[index] - series[index - window]
        result.append(total / window)
    return tuple(result)


def exponential_smoothing(values: Iterable[float], alpha: float) -> tuple[float, ...]:
    """Aplica suavização exponencial simples com estado inicial observado."""
    series = _series(values)
    alpha = float(alpha)
    if not math.isfinite(alpha) or not 0 < alpha <= 1:
        raise ValueError("alpha deve pertencer a (0, 1]")
    result = [series[0]]
    for value in series[1:]:
        result.append(alpha * value + (1 - alpha) * result[-1])
    return tuple(result)


def autocovariance(values: Iterable[float], lag: int = 0, *, unbiased: bool = False) -> float:
    """Calcula autocovariância com média global e normalização explícita."""
    series = _series(values)
    if not isinstance(lag, int) or not 0 <= lag < len(series):
        raise ValueError("lag inválido")
    mean = sum(series) / len(series)
    numerator = sum(
        (series[index] - mean) * (series[index - lag] - mean)
        for index in range(lag, len(series))
    )
    denominator = len(series) - lag if unbiased else len(series)
    return numerator / denominator


def autocorrelation(values: Iterable[float], lag: int = 1) -> float:
    """Normaliza a autocovariância pela variância de lag zero."""
    series = _series(values)
    variance = autocovariance(series)
    if variance == 0:
        raise ValueError("autocorrelação é indefinida para série constante")
    return autocovariance(series, lag) / variance


def linear_trend(values: Iterable[float]) -> tuple[float, float]:
    """Ajusta intercepto e inclinação por mínimos quadrados nos índices."""
    series = _series(values, minimum=2)
    count = len(series)
    mean_x = (count - 1) / 2
    mean_y = sum(series) / count
    denominator = sum((index - mean_x) ** 2 for index in range(count))
    slope = sum((index - mean_x) * (value - mean_y) for index, value in enumerate(series)) / denominator
    return mean_y - slope * mean_x, slope


__all__ = [
    "autocorrelation",
    "autocovariance",
    "differences",
    "exponential_smoothing",
    "linear_trend",
    "moving_average",
]
