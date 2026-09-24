"""Receipt da publicação, independente do provedor."""

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class PublicationManifest:
    dataset: str
    revision: str
    content_sha256: str
    records: int
    provider: str
    status: str = "prepared"

    def to_data(self) -> dict:
        return asdict(self)


def prepare(path: str | Path, dataset: str, revision: str, records: int, provider: str = "huggingface") -> PublicationManifest:
    data = Path(path).read_bytes()
    return PublicationManifest(dataset, revision, hashlib.sha256(data).hexdigest(), records, provider)


def write(manifest: PublicationManifest, destination: str | Path) -> Path:
    path = Path(destination)
    path.write_text(json.dumps(manifest.to_data(), indent=2) + "\n", encoding="utf-8")
    return path
