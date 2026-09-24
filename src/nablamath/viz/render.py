"""Renderização determinística opcional; não executa Blender ou HTML arbitrário."""

from pathlib import Path

from .plot import save_png
from .spec import PlotSpec


def render(spec: PlotSpec, destination: str | Path, *, format: str | None = None) -> Path:
    path = Path(destination)
    selected = format or path.suffix.lstrip(".")
    if selected != "png":
        raise ValueError("O backend local suporta apenas PNG")
    return save_png(spec, path)


__all__ = ["render"]
