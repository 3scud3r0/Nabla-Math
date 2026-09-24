"""Armazenamento SQLite local; falhas e correções futuras exigem novos registros."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from contextlib import closing

from .research import ResearchResult
from .research import calculate


def save_result(path: str | Path, result: ResearchResult) -> bool:
    """Retorna True quando insere, False para repetição idêntica."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result.to_data(), ensure_ascii=False, sort_keys=True)
    with closing(sqlite3.connect(path)) as connection, connection:
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
    if not Path(path).is_file():
        return None
    with closing(sqlite3.connect(path)) as connection, connection:
        try:
            row = connection.execute("SELECT payload FROM results WHERE content_id=?", (identifier,)).fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc):
                return None
            raise
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
    with closing(sqlite3.connect(path)) as connection, connection:
        rows = connection.execute("SELECT payload FROM results ORDER BY content_id").fetchall()
    data = []
    for (raw,) in rows:
        record = json.loads(raw)
        if not verify_record(record):
            raise ValueError("Exportação recusada: registro não passou na reexecução")
        data.append(json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    content = ("\n".join(data) + "\n") if data else ""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    destination.write_bytes(content.encode("utf-8"))
    manifest = {"schema_version": 1, "format": "jsonl", "records": len(data),
                "sha256": digest, "evidence": "exact_rational_reexecution_only",
                "formal_proof": False, "publication": "local_snapshot"}
    destination.with_suffix(destination.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(data), digest


def import_snapshot(path: str | Path, source: str | Path) -> tuple[int, int]:
    """Troca manual entre máquinas: valida tudo antes de inserir atomicamente."""
    source = Path(source)
    if source.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("Snapshot excede limite de 64 MiB")
    manifest_path = source.with_suffix(source.suffix + ".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("format") != "jsonl":
        raise ValueError("Formato de snapshot incompatível")
    content = source.read_bytes()
    import hashlib
    if hashlib.sha256(content).hexdigest() != manifest.get("sha256"):
        raise ValueError("Hash do manifesto não confere")
    records = []
    for line in content.splitlines():
        if len(line) > 1024 * 1024:
            raise ValueError("Registro grande demais")
        item = json.loads(line)
        if not verify_record(item):
            raise ValueError("Registro falhou na reexecução")
        records.append(item)
    if len(records) != manifest.get("records"):
        raise ValueError("Contagem do manifesto não confere")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    inserted = 0
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS results (
            content_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        for item in records:
            payload = json.dumps(item, ensure_ascii=False, sort_keys=True)
            existing = connection.execute("SELECT payload FROM results WHERE content_id=?",
                                          (item["content_id"],)).fetchone()
            if existing and existing[0] != payload:
                raise ValueError("Identificador divergente no banco")
            if not existing:
                connection.execute("INSERT INTO results (content_id,payload) VALUES (?,?)",
                                   (item["content_id"], payload))
                inserted += 1
    return inserted, len(records) - inserted
