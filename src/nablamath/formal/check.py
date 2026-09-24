"""Execução isolada de Lean com timeout e captura de diagnóstico."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

from ..research import ResearchResult
from .translate import lean_source


@dataclass(frozen=True)
class FormalCheck:
    verified: bool
    detail: str
    content_id: str


def verify_with_lean(result: ResearchResult, project: Path, timeout_s: int = 120) -> FormalCheck:
    project = project.resolve()
    if not (project / "lakefile.toml").is_file():
        raise ValueError("Projeto Lean não encontrado")
    if not 1 <= timeout_s <= 900:
        raise ValueError("timeout fora do intervalo")
    with tempfile.TemporaryDirectory(prefix="nablamath-lean-") as directory:
        source = Path(directory) / "Check.lean"
        source.write_text(lean_source(result), encoding="utf-8")
        try:
            process = subprocess.run(["lake", "env", "lean", str(source)], cwd=project,
                                     capture_output=True, text=True, timeout=timeout_s, check=False)
        except FileNotFoundError as exc:
            return FormalCheck(False, "lake não encontrado", result.content_id)
        except subprocess.TimeoutExpired:
            return FormalCheck(False, "timeout", result.content_id)
    if process.returncode:
        return FormalCheck(False, (process.stderr or process.stdout)[-2000:], result.content_id)
    return FormalCheck(True, "Lean verificou a instância racional", result.content_id)


__all__ = ["FormalCheck", "verify_with_lean"]
