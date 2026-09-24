"""Conversão explícita de arrays NumPy para listas JSON serializáveis."""

from __future__ import annotations

from typing import Any


def as_array(values: Any):
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Instale o extra 'viz' para usar o adaptador NumPy") from exc
    array = np.asarray(values)
    if not (np.issubdtype(array.dtype, np.number) and np.isfinite(array).all()):
        raise ValueError("O adaptador aceita somente números finitos")
    return array


def to_data(values: Any) -> dict:
    array = as_array(values)
    return {"shape": list(array.shape), "dtype": str(array.dtype), "values": array.tolist(),
            "backend": "numpy"}


__all__ = ["as_array", "to_data"]
