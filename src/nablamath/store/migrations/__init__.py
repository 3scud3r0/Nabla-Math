"""Transactional SQLite schema migrations."""

from __future__ import annotations

from importlib import import_module
import sqlite3

CURRENT_SCHEMA_VERSION = 1


def migrate(connection: sqlite3.Connection) -> int:
    """Upgrade a database transactionally, refusing unknown future schemas."""
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version > CURRENT_SCHEMA_VERSION:
        raise RuntimeError(
            f"Banco usa schema {version}, superior ao suportado {CURRENT_SCHEMA_VERSION}"
        )
    if version == 0:
        # Version-zero databases created by early alphas may already have the
        # results table. The first migration is intentionally idempotent.
        migration = import_module("nablamath.store.migrations.0001_initial")
        connection.executescript(migration.SQL)
        version = 1
    if version != CURRENT_SCHEMA_VERSION:
        raise RuntimeError(f"Não existe caminho de migração para schema {version}")
    return version


__all__ = ["CURRENT_SCHEMA_VERSION", "migrate"]
