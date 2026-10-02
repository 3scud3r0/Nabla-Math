"""Monotonic reservation ledger for local research resources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceRequest:
    cpu_seconds: int
    memory_bytes: int
    disk_bytes: int = 0
    network_bytes: int = 0

    def __post_init__(self) -> None:
        if any(type(value) is not int or value < 0 for value in self.__dict__.values()):
            raise ValueError("Recursos devem ser inteiros não negativos")


class ResourceManager:
    def __init__(self, capacity: ResourceRequest) -> None:
        self.capacity = capacity
        self.used = ResourceRequest(0, 0, 0, 0)

    def reserve(self, request: ResourceRequest) -> None:
        values = {name: getattr(self.used, name) + getattr(request, name)
                  for name in self.used.__dict__}
        if any(values[name] > getattr(self.capacity, name) for name in values):
            raise RuntimeError("Reserva excede capacidade")
        self.used = ResourceRequest(**values)


__all__ = ["ResourceManager", "ResourceRequest"]
