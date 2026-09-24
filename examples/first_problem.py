"""Exemplo comentado: aritmética exata, condição e registro reproduzível."""

from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

from nablamath.research import calculate
from nablamath.storage import save_result, load_result, verify_record


with TemporaryDirectory() as directory:
    result = calculate("(x+x)/x", {"x": Fraction(3, 2)})
    # x=3/2 satisfaz x≠0. A resposta 2 é uma fração exata, sem arredondamento.
    database = Path(directory) / "results.sqlite3"
    save_result(database, result)
    record = load_result(database, result.content_id)
    assert record is not None and verify_record(record)
    print("Resultado:", result.value, "etapas:", len(result.steps))
    print("Condições:", record["assumptions"])
