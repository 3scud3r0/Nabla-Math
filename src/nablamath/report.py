"""Relatório LaTeX derivado das etapas reais; PDF só após compilação bem-sucedida."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from .expression import to_latex
from .research import ResearchResult


def _escape(text: str) -> str:
    for char, replacement in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                              ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"),
                              ("}", r"\}")):
        text = text.replace(char, replacement)
    return text


def render_tex(result: ResearchResult) -> str:
    lines = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[brazil]{babel}",
        r"\usepackage{amsmath}",
        r"\usepackage[margin=2.5cm]{geometry}",
        r"\begin{document}",
        r"\section*{NablaMath: cálculo rastreável}",
        "Identificador: \\texttt{" + result.content_id + "}.\\par",
        r"\subsection*{Expressão inicial}",
        r"\begin{equation}" + to_latex(result.original) + r"\end{equation}",
        r"\subsection*{Transformações}",
    ]
    if not result.steps:
        lines.append("Nenhuma regra de simplificação aplicável.\\par")
    for index, step in enumerate(result.steps, 1):
        lines.append(r"\paragraph{Passo " + str(index) + ": " + _escape(step.rule) + "}")
        lines.append(r"\begin{equation}" + to_latex(step.before) + " = " + to_latex(step.after) + r"\end{equation}")
        if step.required_nonzero:
            lines.append("Condição: $" + ", ".join(to_latex(x) + r"\ne 0" for x in step.required_nonzero) + "$.\\par")
        lines.append("Regra estrutural aplicada; igualdade numérica conferida para a entrada racional fornecida.\\par")
    lines.append(r"\subsection*{Entradas e resultado}")
    for name, value in sorted(result.values.items()):
        lines.append(r"$\mathrm{" + name.replace("_", "\\_") + "} = " + to_latex_number(value) + "$.\\par")
    lines.append(r"\begin{equation}" + to_latex(result.original) + " = " + to_latex_number(result.value) + r"\end{equation}")
    if result.nonzero:
        lines.append("Hipóteses preservadas: $" + ", ".join(to_latex(x) + r"\ne 0" for x in result.nonzero) + "$.\\par")
    lines.append("Evidência: cálculo racional exato nesta entrada e regras estruturais. Sem prova formal Lean ou validação empírica.\\par")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


def to_latex_number(value) -> str:
    return str(value.numerator) if value.denominator == 1 else rf"\frac{{{value.numerator}}}{{{value.denominator}}}"


def write_report(result: ResearchResult, path: str | Path, compile_pdf: bool = False) -> tuple[Path, Path | None]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_tex(result), encoding="utf-8")
    if not compile_pdf:
        return path, None
    compiler = shutil.which("pdflatex")
    if compiler is None:
        raise RuntimeError("pdflatex não está instalado; o arquivo .tex foi preservado")
    completed = subprocess.run(
        [compiler, "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", path.name],
        cwd=path.parent, capture_output=True, text=True, timeout=60, check=False,
    )
    pdf = path.with_suffix(".pdf")
    if completed.returncode != 0 or not pdf.is_file():
        detail = (completed.stdout + completed.stderr)[-700:].strip()
        raise RuntimeError("Falha ao compilar PDF; consulte o log LaTeX se existir. " + detail)
    return path, pdf
