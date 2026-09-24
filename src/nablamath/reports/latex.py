"""Emissão LaTeX estável a partir do relatório canônico."""

from pathlib import Path

from ..report import render_tex
from .model import Report


def render(report: Report) -> str:
    return render_tex(report.result)


def write(report: Report, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(report), encoding="utf-8")
    return path


__all__ = ["render", "write"]
