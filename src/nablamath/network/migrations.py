"""Registro explícito de migrações; nunca altera objetos históricos in-place."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

Migration = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class MigrationRegistry:
    def __init__(self) -> None:
        self._steps: dict[tuple[str, str], Migration] = {}

    def register(self, source: str, target: str, migration: Migration) -> None:
        if not source or not target or source == target or (source, target) in self._steps:
            raise ValueError("migração inválida ou duplicada")
        self._steps[source, target] = migration

    def migrate(self, data: Mapping[str, Any], target: str) -> dict[str, Any]:
        current = data.get("schema_version")
        if not isinstance(current, str):
            raise ValueError("objeto sem schema_version")
        result = dict(data)
        visited = {current}
        while current != target:
            candidates = sorted((destination, operation) for (source, destination), operation in self._steps.items() if source == current)
            if len(candidates) != 1:
                raise ValueError(f"não há caminho de migração não ambíguo de {current} para {target}")
            destination, operation = candidates[0]
            if destination in visited:
                raise ValueError("ciclo no registro de migrações")
            result = dict(operation(result))
            if result.get("schema_version") != destination:
                raise ValueError("migração não declarou a versão de destino")
            current = destination
            visited.add(current)
        return result


__all__ = ["MigrationRegistry"]
