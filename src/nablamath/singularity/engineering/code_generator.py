"""Patch specifications only; generated code is never executed here."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class FileProposal:
    path: str
    purpose: str
    acceptance_tests: tuple[str, ...]

    def __post_init__(self) -> None:
        path = PurePosixPath(self.path)
        if path.is_absolute() or ".." in path.parts or not self.purpose.strip():
            raise ValueError("Proposta de arquivo insegura")
        if not self.acceptance_tests:
            raise ValueError("Proposta precisa de critério de aceite")


def propose_files(specification: str, paths: tuple[str, ...]) -> tuple[FileProposal, ...]:
    if not specification.strip():
        raise ValueError("Especificação vazia")
    return tuple(FileProposal(path, specification, (f"testar contrato de {path}",)) for path in paths)


__all__ = ["FileProposal", "propose_files"]
