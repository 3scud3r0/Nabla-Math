"""Diferenciação automática direta de funções escalares em números duais."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable


@dataclass(frozen=True)
class Dual:
    primal: float
    tangent: float

    def __add__(self, other: Dual | float) -> Dual:
        b = other if isinstance(other, Dual) else Dual(float(other), 0)
        return Dual(self.primal+b.primal, self.tangent+b.tangent)

    __radd__ = __add__

    def __neg__(self) -> Dual:
        return Dual(-self.primal, -self.tangent)

    def __sub__(self, other: Dual | float) -> Dual:
        return self + -other if isinstance(other, Dual) else self + -float(other)

    def __mul__(self, other: Dual | float) -> Dual:
        b = other if isinstance(other, Dual) else Dual(float(other), 0)
        return Dual(self.primal*b.primal, self.tangent*b.primal+self.primal*b.tangent)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> Dual:
        if type(exponent) is not int or exponent < 0 or exponent > 32:
            raise ValueError("Este backend aceita potência inteira de 0 a 32")
        return Dual(self.primal**exponent,
                    exponent*self.primal**(exponent-1)*self.tangent if exponent else 0)


def jvp(f: Callable[[Dual], Dual], x: float, direction: float = 1) -> tuple[float, float]:
    output = f(Dual(x, direction))
    if not isinstance(output, Dual) or not all(isfinite(v) for v in (output.primal, output.tangent)):
        raise ValueError("Função deve retornar Dual finito")
    return output.primal, output.tangent
