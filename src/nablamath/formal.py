"""Gerador restrito de obrigações racionais Lean e verificador opcional local."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import subprocess
import tempfile

from .expression import Binary, Expr, Number, Symbol
from .research import ResearchResult


def _rational(value: Fraction) -> str:
    numerator = f"({value.numerator} : ℚ)"
    return numerator if value.denominator == 1 else f"({numerator} / ({value.denominator} : ℚ))"


def _term(expr: Expr, values: dict[str, Fraction]) -> str:
    if isinstance(expr, Number):
        return _rational(expr.value)
    if isinstance(expr, Symbol):
        return _rational(values[expr.name])
    assert isinstance(expr, Binary)
    left = _term(expr.left, values)
    right = _term(expr.right, values)
    if expr.op == "**":
        exponent = expr.right.value.numerator  # expoente inteiro, imposto pelo parser
        if exponent < 0:
            return f"(({left}) ^ ({-exponent} : ℕ))⁻¹"
        return f"(({left}) ^ ({exponent} : ℕ))"
    return f"({left} {expr.op} {right})"


def lean_source(result: ResearchResult) -> str:
    """Enuncia a igualdade desta instância; não reivindica prova simbólica geral."""
    values = dict(result.values)
    return ("import Mathlib\n\n"
            f"-- Instância racional {result.content_id}; gerada de AST restrita.\n"
            f"example : {_term(result.original, values)} = {_rational(result.value)} := by\n"
            "  norm_num\n")


@dataclass(frozen=True)
class FormalCheck:
    verified: bool
    detail: str
    content_id: str


def verify_with_lean(result: ResearchResult, project: Path, timeout_s: int = 120) -> FormalCheck:
    """Usa Lake/Lean instalado; mantém arquivos temporários fora do dataset."""
    project = project.resolve()
    if not (project / "lakefile.toml").is_file():
        raise ValueError("Projeto Lean não encontrado")
    with tempfile.TemporaryDirectory(prefix="nablamath-lean-") as directory:
        source = Path(directory) / "Check.lean"
        source.write_text(lean_source(result), encoding="utf-8")
        try:
            process = subprocess.run(["lake", "env", "lean", str(source)], cwd=project,
                                     capture_output=True, text=True, timeout=timeout_s, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return FormalCheck(False, type(exc).__name__, result.content_id)
    if process.returncode:
        return FormalCheck(False, (process.stderr or process.stdout)[-2000:], result.content_id)
    return FormalCheck(True, "Lean verificou a instância racional", result.content_id)
