"""Exibe os estados declarados das fases; não infere conclusão pela presença de arquivos."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/ROADMAP_GLOBAL_RESEARCH.md"


def main() -> None:
    source = DOC.read_text(encoding="utf-8")
    phases = re.findall(r"^- \[([ xX])\] \*\*(F[0-6])\*\* (.+)$", source, re.MULTILINE)
    if len(phases) != 7:
        raise SystemExit(f"Esperadas 7 fases no checklist do roadmap; encontradas {len(phases)}")
    print("Estado declarado no roadmap (não é auditoria científica):")
    for checked, phase, summary in phases:
        status = "marcada" if checked.lower() == "x" else "aberta"
        print(f"{phase}: {status} — {summary}")
    print("Arquivos e critérios de aceite: docs/ROADMAP_GLOBAL_RESEARCH.md")
    print("Nenhuma fase é concluída por contagem ou presença de arquivos.")


if __name__ == "__main__":
    main()
