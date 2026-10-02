"""Exact coordinate Riemannian tensors from a metric's two-jet at a point."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from ..linear_algebra.matrices import Matrix

Tensor2 = tuple[tuple[Fraction, ...], ...]
Tensor3 = tuple[Tensor2, ...]
Tensor4 = tuple[Tensor3, ...]


def _fraction_tensor(value: object) -> object:
    if isinstance(value, (tuple, list)):
        return tuple(_fraction_tensor(item) for item in value)
    return Fraction(value)  # type: ignore[arg-type]


@dataclass(frozen=True)
class MetricJet:
    metric: Tensor2
    first: Tensor3  # first[k][i][j] = ∂_k g_ij
    second: Tensor4  # second[k][l][i][j] = ∂_k ∂_l g_ij

    def __post_init__(self) -> None:
        metric = _fraction_tensor(self.metric)
        first = _fraction_tensor(self.first)
        second = _fraction_tensor(self.second)
        size = len(metric)
        if size < 1 or any(len(row) != size for row in metric):
            raise ValueError("Métrica deve ser quadrada")
        if any(metric[i][j] != metric[j][i] for i in range(size) for j in range(size)):
            raise ValueError("Métrica deve ser simétrica")
        if len(first) != size or any(len(layer) != size or any(len(row) != size for row in layer)
                                     for layer in first):
            raise ValueError("Primeiro jet possui shape inválido")
        if len(second) != size or any(len(layer) != size for layer in second):
            raise ValueError("Segundo jet possui shape inválido")
        if any(len(second[k][l]) != size or any(len(row) != size for row in second[k][l])
               for k in range(size) for l in range(size)):
            raise ValueError("Segundo jet possui shape inválido")
        object.__setattr__(self, "metric", metric)
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "second", second)
        Matrix(metric).inverse()  # reject degenerate metrics

    @property
    def dimension(self) -> int:
        return len(self.metric)


@dataclass(frozen=True)
class RiemannianPoint:
    inverse_metric: Tensor2
    christoffel: Tensor3  # Γ^l_ij
    riemann: Tensor4  # R^l_ijk
    ricci: Tensor2
    scalar_curvature: Fraction


def riemannian_tensors(jet: MetricJet) -> RiemannianPoint:
    n = jet.dimension
    inverse = Matrix(jet.metric).inverse().rows
    gamma = [[[Fraction(0) for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for upper in range(n):
        for left in range(n):
            for right in range(n):
                gamma[upper][left][right] = sum(
                    inverse[upper][middle] * (
                        jet.first[left][right][middle] + jet.first[right][left][middle]
                        - jet.first[middle][left][right]
                    ) / 2 for middle in range(n)
                )
    d_inverse = [[[Fraction(0) for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for derivative in range(n):
        for left in range(n):
            for right in range(n):
                d_inverse[derivative][left][right] = -sum(
                    inverse[left][a] * jet.first[derivative][a][b] * inverse[b][right]
                    for a in range(n) for b in range(n)
                )
    d_gamma = [[[[Fraction(0) for _ in range(n)] for _ in range(n)]
                for _ in range(n)] for _ in range(n)]
    for derivative in range(n):
        for upper in range(n):
            for left in range(n):
                for right in range(n):
                    d_gamma[derivative][upper][left][right] = sum(
                        d_inverse[derivative][upper][middle] * (
                            jet.first[left][right][middle] + jet.first[right][left][middle]
                            - jet.first[middle][left][right]
                        ) / 2 + inverse[upper][middle] * (
                            jet.second[derivative][left][right][middle]
                            + jet.second[derivative][right][left][middle]
                            - jet.second[derivative][middle][left][right]
                        ) / 2 for middle in range(n)
                    )
    riemann = [[[[Fraction(0) for _ in range(n)] for _ in range(n)]
                for _ in range(n)] for _ in range(n)]
    for upper in range(n):
        for vector in range(n):
            for left in range(n):
                for right in range(n):
                    riemann[upper][vector][left][right] = (
                        d_gamma[left][upper][right][vector]
                        - d_gamma[right][upper][left][vector]
                        + sum(gamma[upper][left][middle] * gamma[middle][right][vector]
                              - gamma[upper][right][middle] * gamma[middle][left][vector]
                              for middle in range(n))
                    )
    ricci = [[sum(riemann[upper][left][upper][right] for upper in range(n))
              for right in range(n)] for left in range(n)]
    scalar = sum(inverse[left][right] * ricci[left][right]
                 for left in range(n) for right in range(n))
    return RiemannianPoint(tuple(tuple(row) for row in inverse),
                           _fraction_tensor(gamma), _fraction_tensor(riemann),
                           tuple(tuple(row) for row in ricci), scalar)


__all__ = ["MetricJet", "RiemannianPoint", "riemannian_tensors"]
