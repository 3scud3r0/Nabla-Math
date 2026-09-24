"""Hash canônico de parâmetros JSON e dependências, incluindo versão do algoritmo."""

import hashlib
import json


def provenance_id(version: str, parameters: dict, dependencies: list[str]) -> str:
    if not version:
        raise ValueError("Versão do algoritmo requerida")
    raw = json.dumps({"version": version, "parameters": parameters,
                      "dependencies": sorted(dependencies)}, sort_keys=True,
                     ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()
