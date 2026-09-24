"""Publicação opt-in de snapshots curados; três arquivos em um commit atômico."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from nablamath.dataset.licenses import assess
from nablamath.dataset.deduplicate import normalized_expression
from nablamath.storage import verify_record
from .manifest import PublicationManifest


def validate(snapshot: str | Path, *, repo_id: str, approval: str | Path) -> tuple[PublicationManifest, Path]:
    """Audita os bytes efetivos antes de admitir um envio público."""
    path = Path(snapshot)
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo_id, re.ASCII):
        raise ValueError("Identificador do dataset inválido")
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("Snapshot excede o limite de 64 MiB")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    metadata = json.loads(path.with_suffix(path.suffix + ".manifest.json").read_text(encoding="utf-8"))
    decision = json.loads(Path(approval).read_text(encoding="utf-8"))
    card = path.with_suffix(path.suffix + ".CARD.md")
    if not card.is_file() or not card.read_text(encoding="utf-8").strip():
        raise ValueError("Cartão de dados ausente")
    if (metadata.get("schema_version") != 1 or metadata.get("sha256") != digest
            or metadata.get("publication") != "local_only"):
        raise ValueError("Manifesto de curadoria inválido ou adulterado")
    if (decision.get("approved_for_publication") is not True
            or decision.get("snapshot_sha256") != digest
            or decision.get("dataset_repo") != repo_id
            or not isinstance(decision.get("reviewer"), str)
            or not decision["reviewer"].strip()
            or decision.get("license_id") != metadata.get("license_declaration")):
        raise ValueError("Aprovação explícita não corresponde ao snapshot")
    license_decision = assess(decision["license_id"], redistributable=decision.get("redistributable") is True,
                              attribution=decision.get("attribution", ""))
    if not license_decision.eligible:
        raise ValueError(license_decision.reason)
    if not isinstance(metadata.get("provenance"), str) or not metadata["provenance"].strip():
        raise ValueError("Procedência ausente")
    seen_ids: set[str] = set()
    source_splits: dict[str, str] = {}
    counts = {"train": 0, "validation": 0, "test": 0}
    try:
        lines = raw.decode("utf-8").splitlines()
        for line in lines:
            if len(line.encode("utf-8")) > 1024 * 1024:
                raise ValueError("Registro excede 1 MiB")
            entry = json.loads(line)
            record, split = entry["record"], entry["split"]
            if (split not in counts or not verify_record(record)
                    or entry.get("quality") != "exact_instance_reexecuted"
                    or entry.get("formal_proof") is not False
                    or entry.get("license_declaration") != decision["license_id"]
                    or entry.get("provenance") != metadata["provenance"]):
                raise ValueError("Registro curado não passou na auditoria")
            content_id = record["content_id"]
            source = normalized_expression(record["source"])
            if content_id in seen_ids or (source in source_splits and source_splits[source] != split):
                raise ValueError("Duplicação ou vazamento entre divisões")
            seen_ids.add(content_id)
            source_splits[source] = split
            counts[split] += 1
    except (TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Snapshot malformado") from exc
    if not lines or len(lines) != metadata.get("records") or counts != metadata.get("split_counts"):
        raise ValueError("Contagens do manifesto não conferem")
    return PublicationManifest(repo_id, digest, digest, len(lines), "huggingface"), card


def publish(snapshot: str | Path, *, approval: str | Path, client, repo_id: str,
            operation_factory=None, dry_run: bool = True) -> dict:
    """Executa um commit único; dry_run valida tudo e não toca na rede."""
    manifest, card = validate(snapshot, repo_id=repo_id, approval=approval)
    prefix = f"snapshots/{manifest.content_sha256}"
    outcome = {"manifest": manifest.to_data(), "status": "validated", "paths": [
        f"{prefix}/data.jsonl", f"{prefix}/manifest.json", f"{prefix}/CARD.md"]}
    if dry_run:
        return outcome
    if client is None:
        raise ValueError("Cliente autenticado obrigatório")
    if operation_factory is None:
        from huggingface_hub import CommitOperationAdd
        operation_factory = CommitOperationAdd
    manifest_bytes = (json.dumps(manifest.to_data(), sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    # Usar uma pasta endereçada pelo hash preserva cada versão histórica.
    operations = [operation_factory(path_in_repo=outcome["paths"][0], path_or_fileobj=str(snapshot)),
                  operation_factory(path_in_repo=outcome["paths"][1], path_or_fileobj=manifest_bytes),
                  operation_factory(path_in_repo=outcome["paths"][2], path_or_fileobj=str(card))]
    receipt = client.create_commit(repo_id=repo_id, repo_type="dataset", operations=operations,
                                   commit_message=f"Publish NablaMath curated snapshot {manifest.content_sha256[:12]}")
    return {**outcome, "status": "submitted", "receipt": str(receipt)}
