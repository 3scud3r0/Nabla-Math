"""Especificação serializável de visualização, separada do backend gráfico."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json


@dataclass(frozen=True)
class PlotSpec:
    title: str
    x_label: str
    y_label: str
    x: tuple[float, ...]
    y: tuple[float, ...]
    unit: str = "1"
    source: str = "computed"

    def __post_init__(self) -> None:
        if not self.title or len(self.x) != len(self.y) or not self.x:
            raise ValueError("Série precisa de título e vetores do mesmo tamanho não vazios")
        if any(not isinstance(v, (int, float)) for v in self.x + self.y):
            raise ValueError("Série deve ser numérica")

    def to_data(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_data(), sort_keys=True, ensure_ascii=False)


__all__ = ["PlotSpec"]
