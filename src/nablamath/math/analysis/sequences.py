"""Diagnósticos finitos para sequências reais, sem alegar provas de convergência."""
import math
from collections.abc import Callable


def partial_sums(sequence: Callable[[int], float], count: int) -> tuple[float, ...]:
    if not 0 <= count <= 10_000_000: raise ValueError("count fora do limite")
    total=0.0; result=[]
    for index in range(count):
        value=float(sequence(index))
        if not math.isfinite(value): raise ValueError("termo não finito")
        total+=value; result.append(total)
    return tuple(result)


def cauchy_tail_bound(values: tuple[float, ...], tail: int) -> float:
    if not values or not 1 <= tail <= len(values): raise ValueError("cauda inválida")
    selected=values[-tail:]
    if not all(math.isfinite(value) for value in selected): raise ValueError("valor não finito")
    return max(selected)-min(selected)


def aitken_delta_squared(values: tuple[float, ...]) -> tuple[float | None, ...]:
    if len(values)<3: return ()
    result=[]
    for first,second,third in zip(values[:-2],values[1:-1],values[2:],strict=True):
        denominator=third-2*second+first
        result.append(None if denominator==0 else first-(second-first)**2/denominator)
    return tuple(result)


def monotonicity(values: tuple[float, ...]) -> str:
    if not values: raise ValueError("sequência vazia")
    increasing=all(a<=b for a,b in zip(values,values[1:]))
    decreasing=all(a>=b for a,b in zip(values,values[1:]))
    if increasing and decreasing:return "constant"
    if increasing:return "nondecreasing"
    if decreasing:return "nonincreasing"
    return "none"

__all__=["aitken_delta_squared","cauchy_tail_bound","monotonicity","partial_sums"]
