"""Limites locais que uma tarefa remota nunca pode ampliar."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceBudget:
    cpu_seconds: int = 30
    memory_bytes: int = 256 * 1024 * 1024
    disk_bytes: int = 128 * 1024 * 1024
    network_bytes: int = 0
    wall_seconds: int = 60

    def __post_init__(self) -> None:
        values = (self.cpu_seconds, self.memory_bytes, self.disk_bytes, self.network_bytes, self.wall_seconds)
        if any(not isinstance(value, int) or value < 0 for value in values):
            raise ValueError("limites devem ser inteiros não negativos")
        if self.cpu_seconds > 86_400 or self.wall_seconds > 86_400:
            raise ValueError("uma tarefa não pode reservar mais de um dia")
        if self.memory_bytes > 64 * 1024**3 or self.disk_bytes > 1024**4 or self.network_bytes > 1024**4:
            raise ValueError("reserva excede os limites de segurança")

    def permits(self, requested: "ResourceBudget") -> bool:
        return all(request <= available for request, available in zip(
            (requested.cpu_seconds, requested.memory_bytes, requested.disk_bytes, requested.network_bytes, requested.wall_seconds),
            (self.cpu_seconds, self.memory_bytes, self.disk_bytes, self.network_bytes, self.wall_seconds), strict=True))


__all__ = ["ResourceBudget"]
