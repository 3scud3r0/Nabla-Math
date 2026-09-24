"""Audita presença de caminhos citados no inventário; presença não significa conclusão."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/ROADMAP_GLOBAL_RESEARCH.md"


def main() -> None:
    source = DOC.read_text(encoding="utf-8")
    section = source.split("## 5. Inventário", 1)[1].split("## 6. Checklist", 1)[0]
    candidates = re.findall(r"^\| `([^`]+)` \|", section, re.MULTILINE)
    paths = [item for item in candidates if " ou " not in item and "*" not in item]
    present = [path for path in paths if (ROOT / path).is_file()]
    missing = [path for path in paths if not (ROOT / path).is_file()]
    print(f"Caminhos específicos existentes: {len(present)}/{len(paths)}")
    print("AVISO: um arquivo existente pode estar incompleto; a contagem não mede fases.")
    print("Caminhos ainda não implementados:")
    for path in missing:
        print("-", path)


if __name__ == "__main__":
    main()
