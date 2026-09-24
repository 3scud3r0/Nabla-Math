"""Referência imutável a artefato com autoria declarada."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Artifact:
    sha256: str
    media_type: str
    source: str
    license_declaration: str

    def __post_init__(self) -> None:
        if len(self.sha256) != 64 or any(x not in "0123456789abcdef" for x in self.sha256):
            raise ValueError("SHA-256 inválido")
        if not self.media_type or not self.source or not self.license_declaration:
            raise ValueError("Artefato requer formato, origem e licença declarada")
