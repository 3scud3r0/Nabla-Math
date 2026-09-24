"""Configuração local explícita; não busca credenciais em arquivos implícitos."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalConfig:
    root: Path

    @property
    def database(self) -> Path:
        return self.root / "results.sqlite3"

    @property
    def blob_root(self) -> Path:
        return self.root / "blobs"

    def __post_init__(self) -> None:
        if not str(self.root).strip():
            raise ValueError("Diretório local obrigatório")
