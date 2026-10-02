"""Initial immutable-results schema (SQLite user_version 1)."""

SQL = """
CREATE TABLE IF NOT EXISTS results (
    content_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
PRAGMA user_version = 1;
"""
