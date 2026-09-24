"""Conversão bidirecional estrita da árvore racional do núcleo."""

from fractions import Fraction

from ..expression import Binary, Expr, Number, Symbol, to_data


def from_data(data: dict, depth: int = 0) -> Expr:
    if not isinstance(data, dict) or depth > 64:
        raise ValueError("Árvore inválida ou profunda demais")
    if data.get("kind") == "number" and set(data) == {"kind", "numerator", "denominator"}:
        n, d = data["numerator"], data["denominator"]
        if type(n) is not int or type(d) is not int or d <= 0 or max(abs(n).bit_length(), d.bit_length()) > 4096:
            raise ValueError("Número fora do domínio")
        return Number(Fraction(n, d))
    if data.get("kind") == "symbol" and set(data) == {"kind", "name"}:
        return Symbol(data["name"])
    if data.get("kind") == "binary" and set(data) == {"kind", "op", "left", "right"}:
        return Binary(data["op"], from_data(data["left"], depth+1), from_data(data["right"], depth+1))
    raise ValueError("Formato de expressão desconhecido")


__all__ = ["Expr", "Number", "Symbol", "Binary", "to_data", "from_data"]
