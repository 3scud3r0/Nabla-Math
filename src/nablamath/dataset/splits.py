"""Divisão determinística por família, evitando que a mesma expressão vaze entre splits."""

import hashlib

from .deduplicate import normalized_expression


def split_for(source: str) -> str:
    digest = hashlib.sha256(("family:" + normalized_expression(source)).encode()).digest()[0]
    return "train" if digest < 204 else "validation" if digest < 230 else "test"


def assign(sources: list[str]) -> list[str]:
    return [split_for(source) for source in sources]


__all__ = ["split_for", "assign"]
