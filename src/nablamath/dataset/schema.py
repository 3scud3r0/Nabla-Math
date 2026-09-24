"""Registro de dataset com estados de evidência e direitos declarados."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json


@dataclass(frozen=True)
class DatasetRecord:
    identifier: str
    split: str
    payload: dict
    license_id: str
    provenance: str
    status: str = "executed"
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.identifier or self.split not in {"train", "validation", "test"}:
            raise ValueError("registro requer id e divisão válida")
        if not self.license_id.strip() or not self.provenance.strip():
            raise ValueError("licença e procedência são obrigatórias")
        if self.status not in {"proposed", "executed", "tested", "formal", "quarantined", "retracted"}:
            raise ValueError("estado de dataset desconhecido")

    def to_data(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_data(), sort_keys=True, ensure_ascii=False)


__all__ = ["DatasetRecord"]
