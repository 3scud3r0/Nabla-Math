"""Autenticação simples para implantação inicial; tokens ficam fora do repositório."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac


@dataclass(frozen=True)
class Principal:
    participant_id: str
    scopes: frozenset[str] = frozenset({"read"})


def token_for(secret: str, participant_id: str) -> str:
    if not secret or not participant_id:
        raise ValueError("segredo e participante são obrigatórios")
    return hmac.new(secret.encode(), participant_id.encode(), hashlib.sha256).hexdigest()


def authenticate(secret: str, participant_id: str, token: str, scopes: frozenset[str] | None = None) -> Principal:
    if not hmac.compare_digest(token, token_for(secret, participant_id)):
        raise PermissionError("token inválido")
    return Principal(participant_id, scopes or frozenset({"read"}))


__all__ = ["Principal", "token_for", "authenticate"]
