"""Diretório efêmero; descoberta não implica confiança nem autenticação."""

from __future__ import annotations

from dataclasses import dataclass

from .peer import Peer


@dataclass(frozen=True)
class Announcement:
    peer: Peer
    observed_unix: int
    expires_unix: int

    def __post_init__(self) -> None:
        if self.observed_unix < 0 or self.expires_unix <= self.observed_unix:
            raise ValueError("intervalo de anúncio inválido")
        if self.expires_unix - self.observed_unix > 86_400:
            raise ValueError("anúncio não pode durar mais de um dia")


class PeerDirectory:
    def __init__(self) -> None:
        self._announcements: dict[str, Announcement] = {}

    def announce(self, announcement: Announcement) -> None:
        current = self._announcements.get(announcement.peer.peer_id)
        if current is None or announcement.observed_unix >= current.observed_unix:
            self._announcements[announcement.peer.peer_id] = announcement

    def active(self, now_unix: int, capability: str | None = None) -> tuple[Peer, ...]:
        self._announcements = {key: value for key, value in self._announcements.items()
                               if value.expires_unix > now_unix}
        return tuple(value.peer for key, value in sorted(self._announcements.items())
                     if capability is None or capability in value.peer.capabilities)


__all__ = ["Announcement", "PeerDirectory"]
