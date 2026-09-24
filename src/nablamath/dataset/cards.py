"""Cartão local de dataset; não confere automaticamente direitos de redistribuição."""

from pathlib import Path
import json


def write_dataset_card(manifest_path: Path, destination: Path) -> Path:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = ("sha256", "records", "split_counts", "license_declaration", "provenance")
    if any(key not in manifest for key in required):
        raise ValueError("Manifesto de curadoria incompleto")
    safe = lambda x: str(x).replace("\n", " ").replace("\r", " ")
    card = ("# NablaMath — lote racional local\n\n"
            f"Registros: {manifest['records']}  \n"
            f"SHA-256: `{manifest['sha256']}`  \n"
            f"Divisões: `{json.dumps(manifest['split_counts'], sort_keys=True)}`  \n"
            f"Licença declarada pelo curador: {safe(manifest['license_declaration'])}  \n"
            f"Procedência declarada: {safe(manifest['provenance'])}\n\n"
            "## Escopo e limites\n\n"
            "Contém instâncias aritméticas racionais reexecutadas localmente. "
            "Não demonstra novidade, prova universal, verdade física, titularidade dos direitos "
            "nem ganho de treinamento. Divisões por família ainda exigem análise de vazamento. "
            "Nenhum conteúdo deste arquivo autoriza publicação automática.\n")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(card, encoding="utf-8")
    return destination
