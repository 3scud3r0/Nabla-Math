"""Gráfico 2D opcional, com a especificação exportada junto."""

from pathlib import Path

from .spec import PlotSpec


def save_png(spec: PlotSpec, destination: str | Path) -> Path:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Instale o extra de visualização") from exc
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots()
    axis.plot(spec.x, spec.y)
    axis.set(title=spec.title, xlabel=spec.x_label, ylabel=f"{spec.y_label} [{spec.unit}]")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


__all__ = ["save_png"]
