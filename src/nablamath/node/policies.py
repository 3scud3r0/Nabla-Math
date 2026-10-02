"""Política de ingestão controlada pelo dono do nó."""

from dataclasses import dataclass

from ..network.objects import KnowledgeObject


@dataclass(frozen=True)
class IngestPolicy:
    allowed_types: frozenset[str]
    allowed_licenses: frozenset[str]
    max_object_bytes: int = 1_048_576
    require_dependencies: bool = True

    def __post_init__(self) -> None:
        if not self.allowed_types or not self.allowed_licenses:
            raise ValueError("política precisa permitir ao menos um tipo e uma licença")
        if not 1 <= self.max_object_bytes <= 64 * 1024 * 1024:
            raise ValueError("tamanho máximo fora do intervalo seguro")

    def check(self, item: KnowledgeObject, available_ids: set[str]) -> None:
        if item.object_type not in self.allowed_types:
            raise PermissionError(f"tipo bloqueado pela política local: {item.object_type}")
        if item.license not in self.allowed_licenses:
            raise PermissionError(f"licença bloqueada pela política local: {item.license}")
        if len(item.to_bytes()) > self.max_object_bytes:
            raise PermissionError("objeto excede o limite local")
        missing = set(item.dependencies) - available_ids
        if self.require_dependencies and missing:
            raise PermissionError(f"dependências ausentes: {','.join(sorted(missing))}")


__all__ = ["IngestPolicy"]
