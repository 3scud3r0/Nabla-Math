# NablaMath

## Prévia executável: núcleo local alpha

O repositório agora contém uma **prévia experimental de aritmética racional rastreável** em `src/nablamath/`, instalável localmente com `python -m pip install -e .` ou com os scripts `setup.cmd`/`setup.ps1` no Windows e `setup.sh` em Linux/macOS. Experimente `nabla run "(x+x)/x" --value x=3 --tex report.tex`; o comando mostra etapas, preserva `x != 0`, salva SQLite e gera LaTeX. Veja [instruções e limitações da alpha](docs/CORE_ALPHA.md). Os casos físicos limitados não compõem a plataforma científica ou rede global descrita abaixo.

Este incremento acrescenta [um guia das fórmulas e arquivos executáveis](docs/GUIA_DA_IMPLEMENTACAO.md): unidades SI, álgebra linear exata, RK4, derivação por números duais, fluxo laminar em tubo, coordenador SQLite local com duas verificações, card de dataset e parsers C/C++/Rust para frações canônicas. São recortes testáveis de diferentes fases; nenhuma fase científica/global foi concluída.

[Estado arquivo por arquivo e restrições de conclusão](docs/IMPLEMENTATION_STATUS.md) · auditoria reproduzível: `python tools/roadmap_status.py`.

Verificação de desenvolvimento: `python -m unittest discover -s tests -v`. Lean e compilação PDF são opcionais e não fazem parte da instalação básica. `nabla orbit --altitude-m 400000 --svg orbit.svg` calcula uma órbita circular ideal e gera um diagrama SVG em escala; `nabla formal ID` submete uma instância racional armazenada ao Lean/Mathlib quando Lake estiver instalado; `nabla curate dataset.jsonl --license CC0-1.0 --provenance 'origem controlada'` cria um conjunto local revalidado (a licença é declaração do curador). Veja [limites e comandos novos](docs/INTEGRATIONS_ALPHA.md).

Fluxo laminar delimitado: `nabla fluid --radius-m .01 --length-m 2 --pressure-pa 5 --viscosity-pa-s 1 --density-kg-m3 1000`. Não representa CFD geral.

Intercâmbio manual entre computadores: `nabla export lote.jsonl --db origem.sqlite3` e `nabla import lote.jsonl --db destino.sqlite3`. O importador confere hash, reexecuta os registros e ignora duplicatas idênticas. Ainda não há servidor nem sincronização em tempo real.

## Roteiro para a plataforma de pesquisa distribuída

O [roteiro de implementação, contratos e inventário de arquivos](docs/ROADMAP_GLOBAL_RESEARCH.md) descreve o desenvolvimento progressivo de um pacote Python local, integração Lean/LaTeX, trabalho com ou sem agentes, dados sintéticos curados, site GitHub Pages e uma futura rede de computação voluntária. Veja a [estimativa por marcos e recursos](docs/ESTIMATIVA_EXECUCAO.md) e o [guia de publicação auditada](docs/PUBLISHING.md). **Os exemplos Lean, orbitais e de curadoria locais são limitados; não há serviço global nem dataset publicado.**

Checklist resumido (critérios e caminhos de cada fase constam no roteiro):

- [x] **F0 — roteiro:** documentar arquitetura, ordem, arquivos e critérios de aceitação.
- [ ] **F0 — decisões:** escolher licenças, formatos e políticas de contribuição/segurança.
- [ ] **F1 — biblioteca local (prévia executável):** empacotamento local pip, bootstrap Windows/Linux, CLI, SQLite e exemplo racional; faltam instalação limpa em SOs alvo e estabilidade de API.
- [ ] **F2 — rigor (subconjunto inicial):** Lean/Mathlib para instâncias racionais e dois lemas, LaTeX fonte e hipóteses; faltam provas simbólicas geradas para cada etapa, PDF CI e gráficos auditáveis.
- [ ] **F3 — ciência e agentes (orbital inicial):** modelo analítico de dois corpos com testes de conservação; faltam comparação orbital com referência externa, CFD validado e benchmarks de agentes; há fluxo laminar analítico e trajetória local limitada.
- [ ] **F4 — publicação (curadoria local):** JSONL, manifesto, cartão, auditoria opt-in e workflow diário condicionado a lote aprovado; faltam revisão independente de direitos, publicação real, Parquet e métricas públicas.
- [ ] **F5 — rede global:** coordenação, nós voluntários, verificação independente, autoria e métricas públicas auditáveis.
- [ ] **F6 — interoperabilidade:** protocolo estável, SDKs Rust/C/C++ e avaliação da utilidade dos dados no treinamento.


**Status: inventário de arquivos completo (122/122), prévia local testada; produto global ainda não implementado nem cientificamente validado.**

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

## Scripts históricos

Os [79 scripts Python originais estão organizados em `current scripts/`](current%20scripts/README.md), com as estruturas de versões preservadas. O acervo inclui 50 conteúdos de arquivo distintos; não equivale a uma suíte científica validada ou a uma nova API canônica.
