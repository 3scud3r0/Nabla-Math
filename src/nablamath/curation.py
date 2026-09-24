"""Curadoria reprodutível local para treinamento, sem publicação automática."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
from contextlib import closing

from .dataset.deduplicate import normalized_expression
from .dataset.cards import write_dataset_card
from .storage import verify_record


def curate(path: Path, destination: Path, *, license_id: str, provenance: str) -> dict:
    """Seleciona registros revalidados e separa exemplos pelo texto fonte.

    A licença aqui é uma declaração do curador, não uma verificação jurídica.
    """
    if not license_id.strip() or not provenance.strip():
        raise ValueError("Licença declarada e procedência são obrigatórias")
    with closing(sqlite3.connect(path)) as connection, connection:
        rows = connection.execute("SELECT payload FROM results ORDER BY content_id").fetchall()
    groups: dict[str, dict] = {}
    for (raw,) in rows:
        item = json.loads(raw)
        if not verify_record(item):
            raise ValueError("Registro inválido impede curadoria")
        # Os valores não tornam uma expressão repetida independente para avaliação.
        source = normalized_expression(item["source"])
        bucket = int(source[:8], 16) % 10
        split = "train" if bucket < 8 else "validation" if bucket == 8 else "test"
        groups[item["content_id"]] = {"record": item, "split": split,
                                       "license_declaration": license_id, "provenance": provenance,
                                       "quality": "exact_instance_reexecuted",
                                       "formal_proof": False}
    output = "".join(json.dumps(groups[k], sort_keys=True, ensure_ascii=False) + "\n"
                     for k in sorted(groups))
    digest = hashlib.sha256(output.encode()).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8")
    manifest = {"schema_version": 1, "sha256": digest, "records": len(groups),
                "split_counts": {key: sum(v["split"] == key for v in groups.values())
                                 for key in ("train", "validation", "test")},
                "license_declaration": license_id, "provenance": provenance,
                "publication": "local_only", "warning": "No novelty, data rights, or scientific validity implied."}
    manifest_path = destination.with_suffix(destination.suffix + ".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_dataset_card(manifest_path, destination.with_suffix(destination.suffix + ".CARD.md"))
    return manifest
