"""Registro de backends opcionais sem importar dependências no caminho básico."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util


@dataclass(frozen=True)
class Capability:
    name: str
    package: str
    available: bool
    purpose: str


_CAPABILITIES = (
    Capability("sympy", "sympy", False, "álgebra simbólica externa"),
    Capability("numpy", "numpy", False, "arrays numéricos"),
    Capability("scipy", "scipy", False, "integração e solvers científicos"),
    Capability("matplotlib", "matplotlib", False, "gráficos diagnósticos"),
)


def capabilities() -> tuple[Capability, ...]:
    return tuple(Capability(item.name, item.package, importlib.util.find_spec(item.package) is not None,
                            item.purpose) for item in _CAPABILITIES)


def get(name: str) -> Capability:
    for item in capabilities():
        if item.name == name:
            return item
    raise KeyError(name)


__all__ = ["Capability", "capabilities", "get"]
