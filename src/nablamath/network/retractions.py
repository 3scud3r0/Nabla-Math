"""Retratações imutáveis: não apagam cópias, mas preservam o motivo e substituições."""

from __future__ import annotations

from .objects import KnowledgeObject

REASONS = frozenset({"incorrect", "superseded", "license", "privacy", "malicious", "duplicate"})


def retract(target_id: str, *, reason: str, explanation: str, replacements: tuple[str, ...] = (),
            license: str, provenance: dict[str, object]) -> KnowledgeObject:
    identifiers = (target_id, *replacements)
    if any(len(item) != 64 or any(c not in "0123456789abcdef" for c in item) for item in identifiers):
        raise ValueError("retratação contém identificador inválido")
    if reason not in REASONS or not explanation.strip():
        raise ValueError("motivo suportado e explicação são obrigatórios")
    if tuple(sorted(set(replacements))) != replacements or target_id in replacements:
        raise ValueError("substituições devem estar ordenadas, únicas e não incluir o alvo")
    return KnowledgeObject(
        object_type="retraction", license=license, provenance=provenance,
        dependencies=tuple(sorted(identifiers)),
        payload={"target_id": target_id, "reason": reason, "explanation": explanation,
                 "replacement_ids": list(replacements)},
    )


__all__ = ["REASONS", "retract"]
