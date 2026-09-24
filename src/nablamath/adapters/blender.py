"""Exportador de especificação para Blender; Blender continua uma dependência externa."""

from pathlib import Path
import json

from ..viz.spec import PlotSpec


def write_scene_manifest(spec: PlotSpec, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"format": "nabla-scene-v1", "plot": spec.to_data(),
                                "requires": "Blender adapter", "validated": False},
                               indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


__all__ = ["write_scene_manifest"]
