"""Estados de evidência com força explicitamente separada."""

from dataclasses import dataclass
from enum import Enum


class EvidenceKind(str, Enum):
    COMPUTED = "computed_exact_instance"
    FORMAL = "kernel_checked_formal_statement"
    NUMERICAL = "numerical_with_error"
    EMPIRICAL = "empirical_observation"


@dataclass(frozen=True)
class Evidence:
    kind: EvidenceKind
    statement: str
    artifact_sha256: str
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.statement or len(self.artifact_sha256) != 64 or any(
            ch not in "0123456789abcdef" for ch in self.artifact_sha256
        ):
            raise ValueError("Evidência requer enunciado e SHA-256 hexadecimal")
