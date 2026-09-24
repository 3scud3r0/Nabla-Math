"""Versão de registro e política de migração explícita."""

SCHEMA_VERSION = 1


def require_schema_version(record: dict) -> None:
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Versão do registro incompatível; migração explícita necessária")
