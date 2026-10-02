"""Códigos binários finitos e desigualdade de Kraft exata."""

from fractions import Fraction
from typing import Mapping, TypeVar

T = TypeVar("T")


def is_prefix_free(code: Mapping[T, str]) -> bool:
    words = tuple(code.values())
    if not words or len(set(words)) != len(words) or any(not word or set(word) - {"0", "1"} for word in words):
        raise ValueError("palavras-código binárias, únicas e não vazias são obrigatórias")
    return all(not right.startswith(left) for left in words for right in words if left != right)


def kraft_sum(code: Mapping[T, str]) -> Fraction:
    is_prefix_free(code)  # também valida o formato; Kraft vale mesmo sem prefix-free
    return sum((Fraction(1, 2 ** len(word)) for word in code.values()), Fraction())


def encode(symbols: tuple[T, ...], code: Mapping[T, str]) -> str:
    if not is_prefix_free(code): raise ValueError("código precisa ser livre de prefixo")
    try: return "".join(code[symbol] for symbol in symbols)
    except KeyError as exc: raise ValueError("símbolo sem palavra-código") from exc


def decode(bits: str, code: Mapping[T, str]) -> tuple[T, ...]:
    if not is_prefix_free(code) or set(bits) - {"0", "1"}: raise ValueError("código ou bits inválidos")
    reverse = {word: symbol for symbol, word in code.items()}; buffer = ""; output = []
    for bit in bits:
        buffer += bit
        if buffer in reverse: output.append(reverse[buffer]); buffer = ""
    if buffer: raise ValueError("sequência termina em palavra incompleta")
    return tuple(output)


__all__ = ["decode", "encode", "is_prefix_free", "kraft_sum"]
