"""Contrato de etapa: regra, obrigações de domínio e evidência associada."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StepRecord:
    rule: str
    before: dict
    after: dict
    conditions: tuple[str, ...] = ()
    evidence_sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.rule or not isinstance(self.before, dict) or not isinstance(self.after, dict):
            raise ValueError("Etapa precisa de regra e expressões serializadas")
