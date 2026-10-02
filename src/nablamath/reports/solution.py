"""LaTeX report for an auditable SolutionBundle."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Mapping

from ..entity import ExpressionEntity
from ..expression import to_latex
from ..solution import SolutionBundle


def _escape(text: str) -> str:
    replacements = (
        ("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
        ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
    )
    for char, replacement in replacements:
        text = text.replace(char, replacement)
    return text


def _number(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else rf"\frac{{{value.numerator}}}{{{value.denominator}}}"


def render_solution(entity: ExpressionEntity, bundle: SolutionBundle,
                    values: Mapping[str, Fraction | int | str]) -> str:
    if bundle.entity_id != entity.content_id:
        raise ValueError("SolutionBundle não pertence à entidade fornecida")
    lines = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[brazil]{babel}",
        r"\usepackage{amsmath}",
        r"\usepackage{booktabs}",
        r"\usepackage[margin=2.5cm]{geometry}",
        r"\begin{document}",
        r"\section*{NablaMath SolutionBundle}",
        "Entity ID: \\texttt{" + entity.content_id + "}.\\par",
        "Bundle ID: \\texttt{" + bundle.content_id + "}.\\par",
        "Compiler IR ID: \\texttt{" + bundle.compiler_ir_id + "}.\\par",
        r"\subsection*{Definição semântica}",
        r"\begin{equation}" + to_latex(entity.expression) + r"\end{equation}",
        r"\subsection*{Forma extraída pelo e-graph}",
        r"\begin{equation}" + to_latex(bundle.optimized_expression) + r"\end{equation}",
        r"\subsection*{Instância avaliada}",
    ]
    for name, value in sorted(values.items()):
        rational = value if isinstance(value, Fraction) else Fraction(value)
        lines.append(r"$\mathrm{" + _escape(name) + "}=" + _number(rational) + r"$.\par")
    lines += [
        r"\begin{equation}\mathrm{resultado}=" + _number(bundle.exact_value) + r"\end{equation}",
        r"\subsection*{Hipóteses}",
    ]
    if bundle.assumptions:
        lines.extend(_escape(item) + r".\par" for item in bundle.assumptions)
    else:
        lines.append("Nenhuma hipótese adicional registrada.\\par")
    lines += [
        r"\subsection*{Verificações}",
        r"\begin{tabular}{lll}",
        r"\toprule Método & Resultado & Detalhe \\",
        r"\midrule",
    ]
    for item in bundle.verifications:
        lines.append(_escape(item.method) + " & " + _escape(item.outcome) + " & " + _escape(item.detail) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\subsection*{Limitações}"]
    for limitation in bundle.limitations:
        lines.append(r"\noindent " + _escape(limitation) + r".\par")
    lines += [
        r"\paragraph{Interpretação de evidência}",
        "Um resultado ``passed`` registra somente o método indicado. "
        "Um item ``not\\_requested`` não constitui prova nem falha; indica que a checagem não foi executada.\\par",
        r"\end{document}",
    ]
    return "\n".join(lines) + "\n"


def write_solution_report(entity: ExpressionEntity, bundle: SolutionBundle,
                          values: Mapping[str, Fraction | int | str], destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_solution(entity, bundle, values), encoding="utf-8")
    return path


__all__ = ["render_solution", "write_solution_report"]