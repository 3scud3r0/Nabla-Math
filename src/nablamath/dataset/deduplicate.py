"""Chave estrutural: elimina diferenças de espaços/parênteses redundantes."""

import hashlib
import json

from ..expression import parse_expr, to_data


def normalized_expression(source: str) -> str:
    canonical = json.dumps(to_data(parse_expr(source)), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
