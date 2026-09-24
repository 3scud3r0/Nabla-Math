# NablaMath — status verificável de publicação (24/09/2026)

**Publicação parcial — fonte e documentação no GitHub; acervo binário ainda pendente.** O branch `main` foi verificado com **53 arquivos**: 41 `.py` (40 históricos, 1 importador), 4 `.tex`, 7 `.md` e 1 workflow `.yml`.

Publicado: README com visão final, handoff/arquitetura para outra IA, inventário de 177 arquivos, registro recuperável dos pedidos da conversa, fontes standalone, módulos originais v0.3, motor orbital v0.4, fontes NablaRender v0.7, regressões e exemplos.

**NÃO PUBLICADO NESTE MOMENTO:** o ZIP original de 27,5 MB e os 177 membros extraídos — PDFs, imagens e arquivos históricos restantes não estão no remoto. Não dizer “upload completo” antes de `archive/artifacts/` e `archive/bundles/` existirem e passarem na action.

- [README](../README.md)
- [Handoff da próxima IA](AI_HANDOFF.md)
- [Histórico recuperável](CONVERSATION_FOR_NEXT_AI.md)
- [Inventário dos 177 arquivos](CONTENT_INDEX.md)
- [Publicação segura dos bytes binários restantes](UPLOAD_REMAINING_ARCHIVE.md)
- [Importador pronto](../scripts/import_archive.py)
- [CI para checagem de sintaxe e integridade](../.github/workflows/archive-audit.yml)

O conector GitHub aceita texto UTF-8, mas não transfere diretamente o ZIP/PDF/PNG local. GitHub Actions habilitado não dá acesso automático ao sandbox ChatGPT; use o importador local ou outro canal de transferência binária verificável.

**Validação:** a action passou nos commits após correção do inicializador indevido de NablaRender; o teste automático atual verifica apenas compilação sintática e ZIP SHA/CRC caso presente. **Não representa validação científica, prova de todos os módulos nem validação dos PDFs.**
