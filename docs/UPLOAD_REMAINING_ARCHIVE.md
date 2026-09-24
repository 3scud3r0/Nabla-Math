# Publicar os arquivos binários restantes (177 itens do ZIP histórico)

**Estado:** os commits feitos pela conexão GitHub incluem documentação, fontes `.py` e arquivos `.tex`; o ZIP de 27,5 MB, PDFs, PNG/JPG e demais membros **ainda precisam de upload de bytes**. Uma permissão de GitHub Actions não transfere automaticamente arquivos existentes apenas no sandbox desta conversa para runners do GitHub.

O conector atual de `create_file` recebe **somente texto UTF-8**, de modo que não deve ser usado para tentar escrever arquivos PDF/PNG/ZIP diretamente. A rotina `scripts/import_archive.py` executa no PC do proprietário para manter os 177 arquivos binários e texto com seus bytes originais. O script se recusa a continuar se o ZIP mudar de SHA-256 ou se o Git remoto for inesperado.

## Arquivo original

`NablaMath_Todos_Arquivos_PDFs_Imagens_Codigo_2026-09-23.zip`

SHA-256:
`d1e4d3b27090bd8aedbf626ea4aea07a788b8a8550e85941da4a2022f751f18b`

177 membros, CRC de todos os itens verificado.

Baixe-o pelo link do ChatGPT correspondente à entrega anterior ou pelo pacote `NablaMath_Repositorio_Completo_Para_Publicar.zip`, que contém o ZIP original em `NablaMath_GitHub_Handoff/archive/bundles/`.

## Windows PowerShell

```powershell
git clone https://github.com/3scud3r0/Nabla-Math.git
cd Nabla-Math

# Verificação sem commit nem upload:
python scripts/import_archive.py --zip "C:\\CAMINHO\\NablaMath_Todos_Arquivos_PDFs_Imagens_Codigo_2026-09-23.zip" --verify-only

# Importa todo o acervo e faz push para repositório PUBLICO:
python scripts/import_archive.py --zip "C:\\CAMINHO\\NablaMath_Todos_Arquivos_PDFs_Imagens_Codigo_2026-09-23.zip" --push --confirm-public
```

O importador extrai os membros de `arquivos/` para `archive/artifacts/` e também mantém o ZIP original em `archive/bundles/`. Os dois arquivos da raiz do ZIP (`LEIA-ME.txt` e `MANIFESTO.csv`) são preservados na pasta `archive/artifacts/`. Todos os 177 membros permanecem recuperáveis. Depois, confira no GitHub que aparecem `archive/artifacts/asteria1_extreme_orbital_report.pdf` e `archive/bundles/NablaMath_Todos_Arquivos_PDFs_Imagens_Codigo_2026-09-23.zip`.

**Privacidade:** o GitHub informado é público; revisar imagens/códigos antes de usar `--confirm-public`. Não cole token GitHub no ChatGPT; use Git Credential Manager ou autenticação Git local.

## Conclusão verificável

Só altere este documento para “concluído” quando o repositório remoto apresentar o ZIP e os 177 membros e a action `archive-audit.yml` validar SHA/CRC. Até lá, a publicação é **parcial**, embora o trabalho textual já esteja commitado.
