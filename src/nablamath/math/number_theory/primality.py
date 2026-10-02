"""Deterministic 64-bit Miller–Rabin and bounded exact AKS."""

from __future__ import annotations
import math


def miller_rabin(n: int) -> bool:
    if type(n) is not int or not 0 <= n < 2**64:
        raise ValueError("Miller-Rabin determinístico suporta 0 <= n < 2^64")
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if n in small:
        return True
    if n < 2 or any(n % prime == 0 for prime in small):
        return False
    odd, exponent = n - 1, 0
    while odd % 2 == 0:
        exponent, odd = exponent + 1, odd // 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0:
            continue
        value = pow(base, odd, n)
        if value in (1, n - 1):
            continue
        for _ in range(exponent - 1):
            value = value * value % n
            if value == n - 1:
                break
        else:
            return False
    return True


def _perfect_power(n: int) -> bool:
    def integer_root(value: int, exponent: int) -> int:
        low, high = 1, 1 << ((value.bit_length() + exponent - 1) // exponent)
        while low <= high:
            middle = (low + high) // 2
            power = middle**exponent
            if power <= value:
                low = middle + 1
            else:
                high = middle - 1
        return high

    for exponent in range(2, n.bit_length() + 1):
        root = integer_root(n, exponent)
        if root >= 2 and root**exponent == n:
            return True
    return False


def _order_exceeds(n: int, modulus: int, bound: int) -> bool:
    if math.gcd(n, modulus) != 1:
        return False
    value = 1
    for _ in range(bound):
        value = value * n % modulus
        if value == 1:
            return False
    return True


def _phi(value: int) -> int:
    result, remaining, divisor = value, value, 2
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            while remaining % divisor == 0:
                remaining //= divisor
            result -= result // divisor
        divisor += 1
    return result - result // remaining if remaining > 1 else result


def _cyclic_mul(first: list[int], second: list[int], modulus: int) -> list[int]:
    size, result = len(first), [0] * len(first)
    for left, left_value in enumerate(first):
        for right, right_value in enumerate(second):
            if left_value and right_value:
                index = (left + right) % size
                result[index] = (result[index] + left_value * right_value) % modulus
    return result


def _aks_congruence(n: int, r: int, constant: int) -> bool:
    result, factor = [1] + [0] * (r - 1), [0] * r
    factor[0], factor[1 % r] = constant % n, 1
    exponent = n
    while exponent:
        if exponent & 1:
            result = _cyclic_mul(result, factor, n)
        factor = _cyclic_mul(factor, factor, n)
        exponent //= 2
    expected = [0] * r
    expected[0] = constant % n
    expected[n % r] = (expected[n % r] + 1) % n
    return result == expected


def aks_is_prime(n: int, *, r_limit: int = 4_096,
                 operation_limit: int = 50_000_000) -> bool:
    if type(n) is not int or n < 0:
        raise ValueError("n deve ser inteiro não negativo")
    if n < 2:
        return False
    if _perfect_power(n):
        return False
    bound, r = n.bit_length() ** 2, 2
    while r <= r_limit and not _order_exceeds(n, r, bound):
        divisor = math.gcd(n, r)
        if 1 < divisor < n:
            return False
        r += 1
    if r > r_limit:
        raise RuntimeError("AKS não encontrou r dentro do orçamento")
    if any(1 < math.gcd(n, candidate) < n for candidate in range(2, min(r, n))):
        return False
    if n <= r:
        return True
    maximum = int(math.sqrt(_phi(r)) * n.bit_length())
    if maximum * r * r * n.bit_length() > operation_limit:
        raise RuntimeError("AKS excede o orçamento estimado")
    return all(_aks_congruence(n, r, constant) for constant in range(1, maximum + 1))


__all__ = ["aks_is_prime", "miller_rabin"]
