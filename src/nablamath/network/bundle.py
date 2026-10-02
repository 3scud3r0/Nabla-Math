"""Bundles offline limitados para replicação entre nós por meio escolhido pelo usuário."""

from __future__ import annotations

import json
from pathlib import Path

from .objects import KnowledgeObject, canonical_json
from .store import ContentStore

BUNDLE_VERSION = "nabla-bundle-v1"


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"chave duplicada no bundle: {key}")
        result[key] = value
    return result


def export_bundle(store: ContentStore, object_ids: tuple[str, ...], destination: str | Path) -> Path:
    if not object_ids or tuple(sorted(set(object_ids))) != object_ids:
        raise ValueError("IDs do bundle devem estar ordenados, únicos e não vazios")
    rows = [{"object_id": identifier, "object": store.get(identifier).to_data()} for identifier in object_ids]
    payload = canonical_json({"objects": rows, "version": BUNDLE_VERSION})
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def read_bundle(source: str | Path, *, max_objects: int = 10_000,
                max_bytes: int = 256 * 1024 * 1024) -> tuple[KnowledgeObject, ...]:
    path = Path(source)
    if path.stat().st_size > max_bytes:
        raise ValueError("bundle excede o limite de bytes")
    if max_objects < 1 or max_bytes < 1:
        raise ValueError("limites de bundle devem ser positivos")
    try:
        data = json.loads(path.read_bytes(), object_pairs_hook=_unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("bundle inválido") from exc
    if not isinstance(data, dict) or set(data) != {"objects", "version"} or data["version"] != BUNDLE_VERSION:
        raise ValueError("envelope de bundle não suportado")
    rows = data["objects"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= max_objects:
        raise ValueError("quantidade de objetos fora do limite")
    result = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"object_id", "object"}:
            raise ValueError("entrada de bundle inválida")
        item = KnowledgeObject.from_bytes(canonical_json(row["object"]))
        if row["object_id"] != item.object_id or item.object_id in seen:
            raise ValueError("ID incorreto ou duplicado no bundle")
        seen.add(item.object_id)
        result.append(item)
    return tuple(result)


__all__ = ["BUNDLE_VERSION", "export_bundle", "read_bundle"]
