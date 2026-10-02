"""Objetos de conhecimento imutáveis e endereçados pelo conteúdo.

O formato deliberadamente exclui floats: números aproximados devem declarar valor,
precisão e unidade como texto em um schema de domínio. Isso mantém os hashes
idênticos entre linguagens e plataformas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import unicodedata
from types import MappingProxyType
from typing import Any, Mapping

SCHEMA_VERSION = "nabla-object-v1"
OBJECT_TYPES = frozenset({
    "problem", "conjecture", "attempt", "proof", "counterexample",
    "critique", "experiment", "benchmark", "dataset_manifest",
    "model_evaluation", "verification_receipt", "retraction",
})


def _validate_json(value: Any, path: str = "payload") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise ValueError(f"{path}: floats não são canônicos; use texto com precisão declarada")
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_json(item, f"{path}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{path}: chaves devem ser strings não vazias")
            _validate_json(item, f"{path}.{key}")
        return
    raise ValueError(f"{path}: tipo não serializável: {type(value).__name__}")


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, Mapping):
        normalized = {}
        for key, item in value.items():
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise ValueError("chaves colidem após normalização Unicode")
            normalized[normalized_key] = _normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    return value


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"chave JSON duplicada: {key}")
        result[key] = value
    return result


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _validate_ids(values: tuple[str, ...], label: str) -> None:
    if tuple(sorted(set(values))) != values:
        raise ValueError(f"{label} deve estar ordenado e sem duplicatas")
    if any(len(value) != 64 or any(c not in "0123456789abcdef" for c in value) for value in values):
        raise ValueError(f"{label} contém identificador SHA-256 inválido")


def canonical_json(value: Mapping[str, Any]) -> bytes:
    """Serializa sem ambiguidades para hashing e interoperabilidade."""
    _validate_json(value, "object")
    return json.dumps(_thaw(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class KnowledgeObject:
    object_type: str
    payload: Mapping[str, Any]
    license: str
    provenance: Mapping[str, Any]
    parents: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION
    _object_id: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema não suportado: {self.schema_version}")
        if self.object_type not in OBJECT_TYPES:
            raise ValueError(f"tipo de objeto não suportado: {self.object_type}")
        if not self.license.strip():
            raise ValueError("licença é obrigatória")
        normalized_payload = _normalize(self.payload)
        normalized_provenance = _normalize(self.provenance)
        _validate_json(normalized_payload)
        _validate_json(normalized_provenance, "provenance")
        object.__setattr__(self, "payload", _freeze(normalized_payload))
        object.__setattr__(self, "provenance", _freeze(normalized_provenance))
        _validate_ids(self.parents, "parents")
        _validate_ids(self.dependencies, "dependencies")
        object.__setattr__(self, "_object_id", hashlib.sha256(canonical_json(self.to_data())).hexdigest())

    @property
    def object_id(self) -> str:
        return self._object_id

    def to_data(self) -> dict[str, Any]:
        return {
            "dependencies": list(self.dependencies),
            "license": self.license,
            "object_type": self.object_type,
            "parents": list(self.parents),
            "payload": _thaw(self.payload),
            "provenance": _thaw(self.provenance),
            "schema_version": self.schema_version,
        }

    def to_bytes(self) -> bytes:
        return canonical_json(self.to_data())

    @classmethod
    def from_bytes(cls, raw: bytes) -> "KnowledgeObject":
        try:
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("objeto não contém JSON UTF-8 válido") from exc
        expected = {"dependencies", "license", "object_type", "parents", "payload", "provenance", "schema_version"}
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("campos do objeto não correspondem ao schema v1")
        item = cls(
            object_type=data["object_type"], payload=data["payload"], license=data["license"],
            provenance=data["provenance"], parents=tuple(data["parents"]),
            dependencies=tuple(data["dependencies"]), schema_version=data["schema_version"],
        )
        if item.to_bytes() != raw:
            raise ValueError("objeto não usa a codificação canônica v1")
        return item


__all__ = ["KnowledgeObject", "OBJECT_TYPES", "SCHEMA_VERSION", "canonical_json"]
