"""Teste de integração obrigatório da instância gerada com o Lean no CI."""

from pathlib import Path

from .formal import verify_with_lean
from .research import calculate


def main() -> None:
    for expression, values in [("(x+x)/x", {"x": 3}), ("1/3 + y", {"y": "2/3"})]:
        check = verify_with_lean(calculate(expression, values), Path("lean"))
        if not check.verified:
            raise RuntimeError(f"Falha da verificação Lean: {check.detail}")


if __name__ == "__main__":
    main()
