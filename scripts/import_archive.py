#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import the historical NablaMath archive into the CURRENT Git clone.

Requires Git for Windows, a normal GitHub authentication already configured
on the user's PC, and the original ZIP downloaded from ChatGPT.
No passwords, PATs, GitHub tokens or secrets are passed to this script.
Never runs in CI; a GitHub Actions runner has no access to ChatGPT sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

REPO_URL = "https://github.com/3scud3r0/Nabla-Math.git"
ARCHIVE_NAME = "NablaMath_Todos_Arquivos_PDFs_Imagens_Codigo_2026-09-23.zip"
ARCHIVE_SHA256 = "d1e4d3b27090bd8aedbf626ea4aea07a788b8a8550e85941da4a2022f751f18b"
EXPECTED_MEMBERS = 177

def git(repo: Path, *args: str, capture: bool = False) -> str:
    p = subprocess.run(["git", *args], cwd=repo, text=True, check=True,
                       stdout=subprocess.PIPE if capture else None)
    return (p.stdout or "").strip()

def validate_zip(archive: Path) -> list[zipfile.ZipInfo]:
    if not archive.is_file():
        raise FileNotFoundError(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise ValueError(f"SHA256 diferente: {digest}; esperado: {ARCHIVE_SHA256}")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("CRC invalido")
        members = [m for m in z.infolist() if not m.is_dir()]
        if len(members) != EXPECTED_MEMBERS:
            raise ValueError(f"Esperados {EXPECTED_MEMBERS}; encontrados {len(members)}")
        for m in members:
            p = PurePosixPath(m.filename)
            if p.is_absolute() or ".." in p.parts or "." in p.parts or ":" in m.filename:
                raise ValueError(f"Caminho nao seguro: {m.filename}")
            if stat.S_ISLNK(m.external_attr >> 16):
                raise ValueError(f"Symlink nao permitido: {m.filename}")
    return members

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", dest="archive", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--confirm-public", action="store_true")
    args = parser.parse_args()
    archive = args.archive.expanduser().resolve()
    members = validate_zip(archive)
    print(f"ZIP OK: {len(members)} arquivos; SHA-256 = {ARCHIVE_SHA256}")
    if args.verify_only:
        return
    if args.push and not args.confirm_public:
        parser.error("--push exige --confirm-public: arquivos irao ao GitHub PUBLICO")
    repo = args.repo.expanduser().resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"Use um clone existente de {REPO_URL}: {repo}")
    origin = git(repo, "remote", "get-url", "origin", capture=True)
    if origin not in (REPO_URL, REPO_URL[:-4], "git@github.com:3scud3r0/Nabla-Math.git"):
        raise ValueError(f"Origin inesperado: {origin}")
    if git(repo, "branch", "--show-current", capture=True) != "main":
        raise ValueError("Execute na branch main")
    if git(repo, "status", "--porcelain", capture=True):
        raise ValueError("Worktree suja: faca backup ou commit antes")
    git(repo, "pull", "--ff-only", "origin", "main")
    artifacts = repo / "archive" / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for item in members:
            parts = PurePosixPath(item.filename).parts
            relative = parts[1:] if parts[0] == "arquivos" else parts
            if not relative:
                raise ValueError(f"Membro sem nome: {item.filename}")
            target = artifacts.joinpath(*relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as src, target.open("wb") as dest:
                shutil.copyfileobj(src, dest)
    bundles = repo / "archive" / "bundles"
    bundles.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(archive, bundles / ARCHIVE_NAME)
    (repo / "archive" / "ARCHIVE_SHA256.txt").write_text(
        f"{ARCHIVE_SHA256}  bundles/{ARCHIVE_NAME}\\n", encoding="utf-8")
    git(repo, "add", "archive")
    status = git(repo, "status", "--short", capture=True)
    if not status:
        print("Nenhuma alteracao — arquivo ja presente")
        return
    print(f"Preparados {len(members)} itens originais, alem do ZIP. Revisar publicacao PUBLICA.")
    git(repo, "commit", "-m", "archive: import all 177 recovered files and original ZIP")
    if args.push:
        git(repo, "push", "origin", "main")
        print("PUSH CONCLUIDO — verifique o commit e o arquivo no GitHub")
    else:
        print("COMMIT LOCAL somente. Use git push origin main depois de revisar.")

if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError,
            zipfile.BadZipFile) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)
