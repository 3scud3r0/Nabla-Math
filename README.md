# NablaMath

**Status: acervo histórico em migração; produto final ainda não implementado nem cientificamente validado.**

NablaMath é a visão de um ambiente aberto de matemática simbólica e numérica, autodiferenciação, tensores, otimização, relatividade especial/geral, dinâmica orbital, calculadora rastreável passo a passo, renderização científica e publicação acadêmica em LaTeX. O usuário quer tanto arquitetura modular testável quanto um único arquivo `.py` gerado automaticamente para distribuição.

> **Não confundir demonstrações históricas com modelos certificados, CFD, um Nanite/Cycles completo ou física de plasma validada. Não aumentar o número de páginas repetindo texto.**

## Comece aqui — instruções para a próxima IA

1. [Estado, visão e inventário de implementação](docs/AI_HANDOFF.md).
2. [Arquitetura-alvo e critérios verificáveis](docs/ARCHITECTURE_AND_ACCEPTANCE.md).
3. [Histórico e transcrição recuperável da conversa](docs/CONVERSATION_FOR_NEXT_AI.md).
4. [Índice e manifesto completo dos artefatos](docs/CONTENT_INDEX.md) — publicação de binários pendente enquanto não aparecerem no repositório.
5. [Como executar o importador do acervo original](docs/UPLOAD_REMAINING_ARCHIVE.md).

O acervo originário compreende um ZIP com 177 itens, entre Python, PDFs, PNG/JPG, fontes LaTeX e HTML. **Não presumir que esses arquivos já foram publicados** sem verificação dos caminhos `archive/artifacts/` no GitHub. Não há transcrição literal integral de turnos antigos além do contexto recuperável explicitado na documentação.

## Prioridade de engenharia

Construir uma suíte executável com testes independentes para matemática, relatividade, órbitas, relatórios e renderização. Para relatórios, preservar fontes `.tex`, equações numeradas, derivações únicas, hipótese/unidade/valor substituído e referências do exemplo Asteria-1 e do relatório simbólico v0.3. Para renders, distinguir diagnóstico, aparência estilizada e observável físico.

## GitHub Actions

Habilitar Actions por si só não transfere arquivos locais para o repositório. O status do código/binários deve ser verificado nos commits e nas pastas publicados; não indicar que arquivos não enviados estão disponíveis.

## Descrição de longo prazo

Leia [description.md](description.md) para a visão unificada, os módulos propostos e o diferencial de rastreabilidade científica. O anexo histórico literal de 4.905 linhas encontra-se no arquivo completo gerado nesta conversa, pendente de substituição da versão editorial publicada no GitHub.
