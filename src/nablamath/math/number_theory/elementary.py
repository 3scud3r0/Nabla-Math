"""Algoritmos elementares exatos de teoria dos números."""

from math import isqrt


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r, old_s, s, old_t, t = abs(a), abs(b), 1, 0, 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s * (-1 if a < 0 else 1), old_t * (-1 if b < 0 else 1)


def modular_inverse(value: int, modulus: int) -> int:
    if modulus <= 1: raise ValueError("módulo deve ser maior que um")
    gcd, coefficient, _ = extended_gcd(value, modulus)
    if gcd != 1: raise ValueError("inverso modular não existe")
    return coefficient % modulus


def is_prime(value: int) -> bool:
    if value < 2: return False
    if value % 2 == 0: return value == 2
    for divisor in range(3, isqrt(value) + 1, 2):
        if value % divisor == 0: return False
    return True


def prime_factors(value: int) -> tuple[int, ...]:
    if value == 0: raise ValueError("zero não possui fatoração prima finita")
    factors = []
    if value < 0: factors.append(-1); value = -value
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0: factors.append(divisor); value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1: factors.append(value)
    return tuple(factors)


__all__ = ["extended_gcd", "is_prime", "modular_inverse", "prime_factors"]
