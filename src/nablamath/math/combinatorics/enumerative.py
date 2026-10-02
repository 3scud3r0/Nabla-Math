"""Contagem enumerativa exata para entradas inteiras limitadas."""

from functools import lru_cache
from math import factorial


def binomial(n: int, k: int) -> int:
    if not isinstance(n, int) or not isinstance(k, int) or n < 0: raise ValueError("n e k devem ser inteiros com n não negativo")
    if k < 0 or k > n: return 0
    k = min(k, n - k); result = 1
    for index in range(1, k + 1): result = result * (n - k + index) // index
    return result


def permutations(n: int, k: int | None = None) -> int:
    if not isinstance(n, int) or n < 0: raise ValueError("n deve ser inteiro não negativo")
    k = n if k is None else k
    if not isinstance(k, int) or k < 0 or k > n: return 0
    return factorial(n) // factorial(n - k)


@lru_cache(maxsize=None)
def partition_number(n: int) -> int:
    if not isinstance(n, int) or not 0 <= n <= 10_000: raise ValueError("n fora do limite")
    if n == 0: return 1
    total = 0; index = 1
    while index * (3 * index - 1) // 2 <= n:
        sign = 1 if index % 2 else -1
        for generalized in (index * (3 * index - 1) // 2, index * (3 * index + 1) // 2):
            if generalized <= n: total += sign * partition_number(n - generalized)
        index += 1
    return total


__all__ = ["binomial", "partition_number", "permutations"]
