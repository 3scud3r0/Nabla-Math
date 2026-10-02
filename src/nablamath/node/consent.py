"""Consentimento local explícito, persistido sem habilitar trabalho por padrão."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile


@dataclass(frozen=True)
class Consent:
    contribute: bool = False
    allow_network: bool = False
    allow_on_battery: bool = False
    expires_unix: int | None = None

    def active(self, now_unix: int) -> bool:
        return self.contribute and (self.expires_unix is None or now_unix < self.expires_unix)


class ConsentStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> Consent:
        if not self.path.exists():
            return Consent()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or set(data) != {"allow_network", "allow_on_battery", "contribute", "expires_unix"}:
            raise ValueError("arquivo de consentimento inválido")
        if not all(isinstance(data[key], bool) for key in ("allow_network", "allow_on_battery", "contribute")):
            raise ValueError("flags de consentimento inválidas")
        if data["expires_unix"] is not None and (not isinstance(data["expires_unix"], int) or data["expires_unix"] < 0):
            raise ValueError("expiração de consentimento inválida")
        return Consent(**data)

    def save(self, consent: Consent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".consent-", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(asdict(consent), stream, sort_keys=True, separators=(",", ":"))
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            try: os.unlink(temporary)
            except FileNotFoundError: pass


__all__ = ["Consent", "ConsentStore"]
