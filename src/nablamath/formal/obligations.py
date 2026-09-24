"""Obrigações de prova persistíveis sem confundir proposta com prova."""

from dataclasses import dataclass
from enum import Enum


class ObligationStatus(str, Enum):
    OPEN = "open"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Obligation:
    identifier: str
    statement: str
    status: ObligationStatus = ObligationStatus.OPEN
    reason: str = ""

    def close(self, status: ObligationStatus, reason: str) -> "Obligation":
        if status is ObligationStatus.OPEN or not reason.strip():
            raise ValueError("Fechamento exige estado final e razão")
        return Obligation(self.identifier, self.statement, status, reason)


__all__ = ["Obligation", "ObligationStatus"]
