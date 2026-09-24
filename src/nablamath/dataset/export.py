"""Exportação de snapshot; Parquet quando opcionalmente instalado, JSONL sempre."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .schema import DatasetRecord


def export_jsonl(records: list[DatasetRecord], destination: str | Path) -> dict:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(record.to_json() + "\n" for record in records)
    digest = sha256(text.encode()).hexdigest()
    path.write_bytes(text.encode("utf-8"))
    manifest = {"schema_version": 1, "format": "jsonl", "records": len(records), "sha256": digest,
                "splits": {s: sum(r.split == s for r in records) for s in ("train", "validation", "test")}}
    path.with_suffix(path.suffix + ".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def export_parquet(records: list[DatasetRecord], destination: str | Path) -> Path:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Parquet requer o extra opcional pyarrow") from exc
    rows = [{**r.to_data(), "payload_json": json.dumps(r.payload, sort_keys=True)} for r in records]
    pq.write_table(pa.Table.from_pylist(rows), destination)
    return Path(destination)


__all__ = ["export_jsonl", "export_parquet"]
