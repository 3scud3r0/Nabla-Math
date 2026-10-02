"""Congruências lineares e teorema chinês dos restos exatos."""

from math import gcd
from .elementary import extended_gcd


def chinese_remainder(congruences: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    if not congruences: raise ValueError("sistema vazio")
    residue, modulus = 0, 1
    for next_residue, next_modulus in congruences:
        if next_modulus <= 0: raise ValueError("módulos devem ser positivos")
        next_residue %= next_modulus
        common, coefficient, _ = extended_gcd(modulus, next_modulus)
        difference = next_residue - residue
        if difference % common: raise ValueError("sistema de congruências incompatível")
        reduced = next_modulus // common
        step = (difference // common * coefficient) % reduced
        residue += modulus * step
        modulus *= reduced
        residue %= modulus
    return residue, modulus


def solve_linear_congruence(a: int, b: int, modulus: int) -> tuple[int, ...]:
    if modulus <= 0: raise ValueError("módulo deve ser positivo")
    common = gcd(a, modulus)
    if b % common: return ()
    base, reduced_modulus = chinese_remainder(((b // common * pow(a // common, -1, modulus // common), modulus // common),))
    return tuple(sorted((base + index * reduced_modulus) % modulus for index in range(common)))


__all__ = ["chinese_remainder", "solve_linear_congruence"]
