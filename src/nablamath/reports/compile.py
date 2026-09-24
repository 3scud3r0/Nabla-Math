"""Compilador LaTeX opt-in sem execução de comandos fornecidos pelo usuário."""

from pathlib import Path
import shutil
import subprocess


def compile_tex(source: str | Path, *, timeout_s: int = 60) -> Path:
    path = Path(source).resolve()
    compiler = shutil.which("pdflatex")
    if compiler is None:
        raise RuntimeError("pdflatex não está instalado")
    if timeout_s < 1 or timeout_s > 600:
        raise ValueError("timeout fora do intervalo")
    command = [compiler, "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", path.name]
    completed = subprocess.run(command, cwd=path.parent, capture_output=True, text=True,
                                timeout=timeout_s, check=False)
    output = path.with_suffix(".pdf")
    if completed.returncode != 0 or not output.is_file():
        raise RuntimeError((completed.stdout + completed.stderr)[-2000:])
    return output


__all__ = ["compile_tex"]
