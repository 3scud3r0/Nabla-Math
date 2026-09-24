"""Armazenamento SQLite local; falhas e correções futuras exigem novos registros."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .research import ResearchResult
from .research import calculate


def save_result(path: str | Path, result: ResearchResult) -> bool:
    """Retorna True quando insere, False para repetição idêntica."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result.to_data(), ensure_ascii=False, sort_keys=True)
    with sqlite3.connect(path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS results (
                content_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        existing = connection.execute("SELECT payload FROM results WHERE content_id=?", (result.content_id,)).fetchone()
        if existing is not None:
            if existing[0] != payload:
                raise ValueError("Colisão de identificador com conteúdo divergente")
            return False
        connection.execute("INSERT INTO results (content_id, payload) VALUES (?, ?)", (result.content_id, payload))
        return True


def load_result(path: str | Path, identifier: str) -> dict | None:
    with sqlite3.connect(path) as connection:
        row = connection.execute("SELECT payload FROM results WHERE content_id=?", (identifier,)).fetchone()
    return json.loads(row[0]) if row else None


def verify_record(payload: dict) -> bool:
    """Reexecuta a trajetória; rejeita qualquer campo ou hash adulterado."""
    try:
        expected = calculate(payload["source"], payload["values"]).to_data()
    except (KeyError, ValueError, ArithmeticError, TypeError):
        return False
    return expected == payload


def export_verified(path: str | Path, destination: str | Path) -> tuple[int, str]:
    """Snapshot local JSONL revalidado; não o publica automaticamente."""
    import hashlib

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        rows = connection.execute("SELECT payload FROM results ORDER BY content_id").fetchall()
    data = []
    for (raw,) in rows:
        record = json.loads(raw)
        if not verify_record(record):
            raise ValueError("Exportação recusada: registro não passou na reexecução")
        data.append(json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    content = ("\n".join(data) + "\n") if data else ""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    destination.write_text(content, encoding="utf-8")
    manifest = {"schema_version": 1, "format": "jsonl", "records": len(data),
                "sha256": digest, "evidence": "exact_rational_reexecution_only",
                "formal_proof": False, "publication": "local_snapshot"}
    destination.with_suffix(destination.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(data), digest
