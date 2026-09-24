"""Expressões racionais exatas e parser de uma sintaxe aritmética restrita."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from fractions import Fraction
import re
from typing import Mapping, TypeAlias


_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")


class DomainError(ValueError):
    """Uma entrada saiu do domínio de uma expressão."""


@dataclass(frozen=True)
class Number:
    value: Fraction


@dataclass(frozen=True)
class Symbol:
    name: str

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.name):
            raise ValueError("Nome de símbolo inválido")


@dataclass(frozen=True)
class Binary:
    op: str
    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if self.op not in {"+", "-", "*", "/", "**"}:
            raise ValueError("Operador inválido")


Expr: TypeAlias = Number | Symbol | Binary


def parse_expr(source: str) -> Expr:
    """Analisa inteiros, símbolos, + - * / e potências inteiras; nunca chama eval."""
    if len(source) > 4096:
        raise ValueError("Expressão grande demais")
    try:
        parsed = ast.parse(source.replace("^", "**"), mode="eval")
    except SyntaxError as exc:
        raise ValueError("Sintaxe matemática inválida") from exc
    return _convert(parsed.body, depth=0)


def _convert(node: ast.AST, depth: int) -> Expr:
    if depth > 64:
        raise ValueError("Expressão profunda demais")
    if isinstance(node, ast.Constant) and type(node.value) is int:
        if abs(node.value).bit_length() > 4096:
            raise ValueError("Inteiro grande demais")
        return Number(Fraction(node.value))
    if isinstance(node, ast.Name):
        return Symbol(node.id)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _convert(node.operand, depth + 1)
        return value if isinstance(node.op, ast.UAdd) else Binary("*", Number(Fraction(-1)), value)
    if isinstance(node, ast.BinOp):
        operators = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Pow: "**"}
        op = operators.get(type(node.op))
        if op is None:
            raise ValueError("Operador não permitido")
        left = _convert(node.left, depth + 1)
        if op == "**":
            exponent = node.right
            sign = 1
            if isinstance(exponent, ast.UnaryOp) and isinstance(exponent.op, (ast.UAdd, ast.USub)):
                sign = -1 if isinstance(exponent.op, ast.USub) else 1
                exponent = exponent.operand
            if not isinstance(exponent, ast.Constant) or type(exponent.value) is not int or abs(exponent.value) > 32:
                raise ValueError("Potências exigem expoente inteiro entre -32 e 32")
            right = Number(Fraction(sign * exponent.value))
        else:
            right = _convert(node.right, depth + 1)
        return Binary(op, left, right)
    raise ValueError("Somente aritmética racional e símbolos são permitidos")


def evaluate(expr: Expr, values: Mapping[str, Fraction]) -> Fraction:
    if isinstance(expr, Number):
        return expr.value
    if isinstance(expr, Symbol):
        if expr.name not in values:
            raise ValueError(f"Falta valor para {expr.name}")
        return values[expr.name]
    a, b = evaluate(expr.left, values), evaluate(expr.right, values)
    if expr.op == "+":
        return a + b
    if expr.op == "-":
        return a - b
    if expr.op == "*":
        return a * b
    if expr.op == "/":
        if b == 0:
            raise DomainError("Divisão por zero")
        return a / b
    if a == 0 and b <= 0:
        raise DomainError("Potência não positiva de zero tem domínio indefinido neste núcleo")
    return a ** b.numerator


def render(expr: Expr) -> str:
    if isinstance(expr, Number):
        return str(expr.value)
    if isinstance(expr, Symbol):
        return expr.name
    return f"({render(expr.left)} {expr.op} {render(expr.right)})"


def to_data(expr: Expr) -> dict:
    if isinstance(expr, Number):
        return {"kind": "number", "numerator": expr.value.numerator, "denominator": expr.value.denominator}
    if isinstance(expr, Symbol):
        return {"kind": "symbol", "name": expr.name}
    return {"kind": "binary", "op": expr.op, "left": to_data(expr.left), "right": to_data(expr.right)}


def to_latex(expr: Expr) -> str:
    if isinstance(expr, Number):
        n, d = expr.value.numerator, expr.value.denominator
        return str(n) if d == 1 else rf"\frac{{{n}}}{{{d}}}"
    if isinstance(expr, Symbol):
        escaped = expr.name.replace("_", "\\_")
        return rf"\mathrm{{{escaped}}}"
    a, b = to_latex(expr.left), to_latex(expr.right)
    if expr.op == "/":
        return rf"\frac{{{a}}}{{{b}}}"
    if expr.op == "**":
        return rf"\left({a}\right)^{{{b}}}"
    operator = r"\cdot" if expr.op == "*" else expr.op
    return rf"\left({a} {operator} {b}\right)"
