"""Raiz Merkle determinística para lotes locais; hash não autentica emissor."""

import hashlib


def merkle_root(digests: list[str]) -> str:
    if not digests:
        return hashlib.sha256(b"NablaMath-empty-v1").hexdigest()
    if len(set(digests)) != len(digests):
        raise ValueError("Identificador duplicado no lote")
    for digest in digests:
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("SHA-256 inválido")
    level = [hashlib.sha256(b"\x00" + bytes.fromhex(d)).digest() for d in sorted(digests)]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(b"\x01"+level[i]+level[i+1]).digest()
                 for i in range(0, len(level), 2)]
    return level[0].hex()
