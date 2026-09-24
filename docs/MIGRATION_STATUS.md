# NablaMath — status verificável de publicação (24/09/2026)

**Publicação GitHub parcial.** O repo contém neste momento 35 arquivos verificados no branch `main`: 23 `.py`, 4 `.tex`, 7 `.md`, 1 `.yml`. Destes 23 Python, 22 são históricos e 1 é o importador. Documentação, código standalone multímódulos, NablaRender v0.7 e LaTeX reais estão publicamente disponíveis.

**AINDA NÃO PUBLICADOS:** o ZIP original de 27,5 MB nem os 177 membros extraídos; portanto PDFs, PNG/JPG e parte do código histórico ainda não constam do remoto. Não dizer “upload completo” até `archive/artifacts/` e `archive/bundles/` existirem no GitHub.

- [README](../README.md)
- [Handoff para a próxima IA](AI_HANDOFF.md)
- [Histórico disponível da conversa](CONVERSATION_FOR_NEXT_AI.md)
- [Inventário dos 177 itens recuperados](CONTENT_INDEX.md)
- [Publicação segura do ZIP e de todos os 177 membros](UPLOAD_REMAINING_ARCHIVE.md)
- [Importador já presente no GitHub](../scripts/import_archive.py)

O conector usado escreve arquivos UTF-8, mas não tem acesso direto aos bytes binários montados no sandbox. GitHub Actions habilitado **não** permite ler os arquivos locais desta conversa. Para completar o upload com SHA exato, o proprietário deve executar `scripts/import_archive.py` com o ZIP local no seu Git autenticado, ou conectar outro sistema de transferência binária verificável.

A ação `archive-audit.yml` faz verificação de sintaxe e, quando o ZIP chegar ao repositório, SHA-256, 177 membros e CRC. Não substitui suite de testes matemáticos/científicos.
