"""Interface de terminal local; nenhuma chamada remota nem dependência de IA."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import sys

from . import __version__
from .curation import curate
from .expression import DomainError, render
from .formal import verify_with_lean
from .orbits import earth_circular_orbit
from .report import write_report
from .research import calculate
from .storage import export_verified, import_snapshot, load_result, save_result, verify_record


def _assignment(text: str) -> tuple[str, Fraction]:
    name, separator, raw = text.partition("=")
    if not separator or not name.isidentifier() or len(raw) > 256:
        raise argparse.ArgumentTypeError("Use nome=inteiro ou nome=numerador/denominador")
    try:
        return name, Fraction(raw)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError("Valor racional inválido") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nabla", description="NablaMath: núcleo local de cálculo rastreável")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Mostrar ambiente e integrações opcionais")
    run = commands.add_parser("run", help="Executar expressão racional com etapas")
    run.add_argument("expression", help='Exemplo: "(x+x)/x"')
    run.add_argument("--value", action="append", type=_assignment, default=[], metavar="X=3")
    run.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    run.add_argument("--tex", type=Path)
    run.add_argument("--pdf", action="store_true", help="Compilar --tex com pdflatex")
    show = commands.add_parser("show", help="Consultar registro pelo identificador")
    show.add_argument("identifier")
    show.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    verify = commands.add_parser("verify", help="Reexecutar um registro armazenado")
    verify.add_argument("identifier")
    verify.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    export = commands.add_parser("export", help="Exportar registros revalidados em JSONL")
    export.add_argument("destination", type=Path)
    export.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    import_cmd = commands.add_parser("import", help="Importar snapshot local após hash e reexecução")
    import_cmd.add_argument("source", type=Path)
    import_cmd.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    curated = commands.add_parser("curate", help="Criar dataset local com proveniência e divisões")
    curated.add_argument("destination", type=Path)
    curated.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    curated.add_argument("--license", required=True, help="Declaração fornecida pelo curador")
    curated.add_argument("--provenance", required=True)
    orbit = commands.add_parser("orbit", help="Órbita terrestre circular ideal em unidades SI")
    orbit.add_argument("--altitude-m", type=float, required=True)
    formal = commands.add_parser("formal", help="Provar no Lean uma instância racional armazenada")
    formal.add_argument("identifier")
    formal.add_argument("--db", type=Path, default=Path(".nabla/results.sqlite3"))
    formal.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[2] / "lean")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            print(json.dumps({"version": __version__, "python": sys.version.split()[0],
                              "pdflatex_command_available": shutil.which("pdflatex") is not None,
                              "lean_command_available": shutil.which("lean") is not None}, ensure_ascii=False))
            return 0
        if args.command == "orbit":
            print(json.dumps(earth_circular_orbit(args.altitude_m).summary(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "curate":
            print(json.dumps(curate(args.db, args.destination, license_id=args.license,
                                    provenance=args.provenance), ensure_ascii=False, indent=2))
            return 0
        if args.command == "import":
            inserted, repeated = import_snapshot(args.db, args.source)
            print(f"Importados: {inserted}; duplicados idênticos: {repeated}")
            return 0
        if args.command == "formal":
            payload = load_result(args.db, args.identifier)
            if payload is None or not verify_record(payload):
                raise ValueError("Registro inexistente ou inválido")
            result = calculate(payload["source"], payload["values"])
            check = verify_with_lean(result, args.project)
            print(json.dumps(check.__dict__, ensure_ascii=False))
            return 0 if check.verified else 1
        if args.command == "show":
            payload = load_result(args.db, args.identifier)
            if payload is None:
                print("Registro não encontrado", file=sys.stderr)
                return 1
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if args.command == "verify":
            payload = load_result(args.db, args.identifier)
            valid = payload is not None and verify_record(payload)
            print("Reexecução exata:", "válida" if valid else "inválida ou ausente")
            return 0 if valid else 1
        if args.command == "export":
            count, digest = export_verified(args.db, args.destination)
            print("Snapshot local:", args.destination, "registros:", count, "sha256:", digest)
            return 0
        if args.pdf and args.tex is None:
            parser.error("--pdf requer --tex")
        values = dict(args.value)
        if len(values) != len(args.value):
            parser.error("Cada símbolo deve ter um valor único")
        result = calculate(args.expression, values)
        created = save_result(args.db, result)
        print("ID:", result.content_id)
        print("Inicial:", render(result.original))
        for step in result.steps:
            print(f"{step.rule}: {render(step.before)} -> {render(step.after)}")
        for assumption in result.to_data()["assumptions"]:
            print("Hipótese:", assumption)
        print("Resultado exato:", result.value)
        print("Banco:", args.db, "(novo)" if created else "(já registrado)")
        if args.tex is not None:
            tex, pdf = write_report(result, args.tex, args.pdf)
            print("LaTeX:", tex)
            if pdf:
                print("PDF:", pdf)
        return 0
    except (ValueError, ArithmeticError, RuntimeError, OSError, DomainError) as exc:
        print("Erro:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
