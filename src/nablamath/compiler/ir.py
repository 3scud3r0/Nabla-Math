"""Backend-neutral SSA-like IR for NablaMath arithmetic expressions.

The IR is deliberately tiny: every instruction references only earlier instruction
IDs, common subexpressions are interned, and the complete program has a stable
content hash. Backends may execute the same program exactly (Python/Fraction)
or approximately (accelerators using floating-point arrays).
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Mapping

from ..expression import Binary, Expr, Number, Symbol


@dataclass(frozen=True)
class Instruction:
    id: int
    op: str
    args: tuple[int, ...] = ()
    value: Fraction | str | None = None

    def to_data(self) -> dict[str, object]:
        value: object = self.value
        if isinstance(value, Fraction):
            value = {"numerator": value.numerator, "denominator": value.denominator}
        return {"id": self.id, "op": self.op, "args": list(self.args), "value": value}


@dataclass(frozen=True)
class Program:
    symbols: tuple[str, ...]
    instructions: tuple[Instruction, ...]
    output: int
    schema_version: int = 1

    def validate(self) -> None:
        if not self.instructions:
            raise ValueError("Programa vazio")
        ids = {instruction.id for instruction in self.instructions}
        if ids != set(range(len(self.instructions))):
            raise ValueError("IDs da IR devem ser densos e começar em zero")
        for instruction in self.instructions:
            if instruction.op in {"number", "symbol"}:
                if instruction.args:
                    raise ValueError("Literal/símbolo não pode ter argumentos")
            elif instruction.op not in {"+", "-", "*", "/", "**"} or len(instruction.args) != 2:
                raise ValueError(f"Instrução inválida: {instruction.op}")
            if any(arg >= instruction.id or arg < 0 for arg in instruction.args):
                raise ValueError("IR não está em ordem topológica")
            if instruction.op == "symbol" and instruction.value not in self.symbols:
                raise ValueError("Símbolo da instrução não está declarado")
        if self.output not in ids:
            raise ValueError("Saída da IR inexistente")

    def to_data(self) -> dict[str, object]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "symbols": list(self.symbols),
            "instructions": [instruction.to_data() for instruction in self.instructions],
            "output": self.output,
        }

    @property
    def content_id(self) -> str:
        canonical = json.dumps(self.to_data(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def lower_expr(expr: Expr) -> Program:
    """Lower an expression to deterministic topological IR with structural CSE."""
    symbols: set[str] = set()

    def collect(node: Expr) -> None:
        if isinstance(node, Symbol):
            symbols.add(node.name)
        elif isinstance(node, Binary):
            collect(node.left)
            collect(node.right)

    collect(expr)
    declared = tuple(sorted(symbols))
    memo: dict[Expr, int] = {}
    instructions: list[Instruction] = []

    def emit(node: Expr) -> int:
        existing = memo.get(node)
        if existing is not None:
            return existing
        if isinstance(node, Number):
            instruction = Instruction(len(instructions), "number", value=node.value)
        elif isinstance(node, Symbol):
            instruction = Instruction(len(instructions), "symbol", value=node.name)
        else:
            left = emit(node.left)
            right = emit(node.right)
            instruction = Instruction(len(instructions), node.op, (left, right))
        instructions.append(instruction)
        memo[node] = instruction.id
        return instruction.id

    output = emit(expr)
    program = Program(declared, tuple(instructions), output)
    program.validate()
    return program


def bind_symbols(program: Program, values: Mapping[str, object]) -> tuple[object, ...]:
    missing = [name for name in program.symbols if name not in values]
    extra = sorted(set(values) - set(program.symbols))
    if missing:
        raise ValueError("Símbolos sem valor: " + ", ".join(missing))
    if extra:
        raise ValueError("Símbolos desconhecidos: " + ", ".join(extra))
    return tuple(values[name] for name in program.symbols)


__all__ = ["Instruction", "Program", "lower_expr", "bind_symbols"]