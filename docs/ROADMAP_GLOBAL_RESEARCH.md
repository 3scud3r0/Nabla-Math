# NablaMath — roteiro executável para pesquisa distribuída

**Estado:** inventário de arquivos presente (122/122) e incrementos locais testados; fases ainda não concluídas. **Revisão:** 2026-09-24. **Base histórica:** `main` em `d1e20635edd0b54c72a1d50d1235d9fa7a610c99`.

Este documento orienta pessoas e agentes que vão transformar o acervo histórico em um pacote Python instalável, uma plataforma de pesquisa local e, progressivamente, uma rede aberta de trabalho científico. Consulte também `docs/AI_HANDOFF.md` e `docs/ARCHITECTURE_AND_ACCEPTANCE.md`. A pasta `current scripts/` contém versões históricas; a presença dos caminhos abaixo foi automatizada, mas nenhum deles deve ser anunciado como fase completa sem passar pelos testes, revisão científica e publicação.

**Prévia implementada nesta branch:** `src/nablamath/` oferece parser aritmético limitado, regras com condição, avaliação racional, banco SQLite, exportação local JSONL e LaTeX, adaptadores opcionais, relatórios, visualização, contratos de dataset e ponte formal modular. O site em `website/` é estático com métricas zero explicitamente rotuladas. Serviços locais opt-in usam SQLite e HMAC, sem publicação automática. Consulte `docs/CORE_ALPHA.md` e `docs/IMPLEMENTATION_STATUS.md`. A tabela abaixo continua descrevendo o **destino arquitetural**; presença não significa conclusão.

## 1. Objetivo e limites

Um problema pode gerar expressões, deduções, resultados numéricos, experimentos, dados, provas Lean, figuras, relatórios LaTeX e trajetórias para treinamento de modelos. Cada artefato registra a origem, as hipóteses, as versões das ferramentas, o tipo de evidência e os limites de validade. Pessoas podem executar tarefas localmente sem IA ou usar agentes submetidos às mesmas interfaces e verificações. Participantes podem optar por contribuir com resultados a um serviço global.

“De A a Z” significa cobertura crescente de uma taxonomia versionada de domínios e problemas, não enumeração finita de toda a matemática, prova de todas as conjecturas ou garantia de verdade física. O valor do dataset deve ser medido por utilidade em tarefas futuras, diversidade, novidade, revisão e reprodutibilidade; volume de arquivos e quantidade de teoremas triviais não são substitutos.

Não usar a expressão “provado” para resultado numérico ou empírico. Lean verifica uma proposição formal sob seus axiomas e hipóteses; não verifica automaticamente que a tradução da pergunta foi fiel ou que um modelo físico corresponde ao mundo. Dados, simuladores, renderizações e relatórios trazem estados de evidência distintos. Computação voluntária não confere confiança por si: resultados externos exigem verificação independente.

## 2. Ciclo de pesquisa e estados

1. **Definir:** registrar enunciado, domínio, unidades, hipótese, autor/origem e licença.
2. **Selecionar:** priorizar lacunas da taxonomia, relevância científica, diversidade e orçamento.
3. **Executar:** calcular ou propor provas/experimentos; salvar também tentativas falhas úteis.
4. **Verificar:** reexecutar, testar domínios e unidades, validar certificado formal, comparar evidências; quarentenar contribuições suspeitas.
5. **Curar:** deduplicar, pontuar novidade/utilidade, revisar enunciados e remover dados sem direitos de redistribuição.
6. **Publicar:** criar snapshot imutável com manifesto, hashes, versão e dataset card; exportar lotes elegíveis, preferencialmente diários, ao Hugging Face.
7. **Reutilizar:** agentes e pessoas recuperam trabalho anterior, criam novas tarefas e registram quais fontes usaram.

Estados obrigatórios: `proposto`, `executado`, `testado`, `prova_verificada`, `corroborado_empiricamente`, `refutado`, `inconclusivo`, `retratado`. Um estado não substitui os outros; cada um contém sua evidência e data. Imutabilidade do histórico de eventos não impede retratação ou correção com novo evento.

## 3. Contratos antes dos algoritmos

Cada registro tem `schema_version`, `id` por hash do conteúdo canônico, `created_at`, `parents`, `problem_id`, domínio/taxonomia, enunciado legível e formal quando houver, hipóteses, tipos, unidades, proveniência de entradas, licenças, referências, executor, versões fixadas de código e dependências, ambiente, semente aleatória, orçamento, código ou instrução executada, resultados, tolerâncias/erros, testes, identificadores de provas, avaliações humanas, estado, assinatura opcional e política de visibilidade. O conteúdo canônico e a identidade de quem contribuiu são conceitos diferentes; nunca usar o hash como prova de autoria ou de correção.

Exportar formatos interoperáveis JSON e Parquet, além de fonte `.lean`, `.tex` e metadados dos arquivos binários; especificar normalização, precisão, encoding e migrações. Reservar divisões de treino/validação/teste por famílias de problemas e tempo, com controle de vazamento e duplicatas. Agentes registram prompts e respostas somente quando houver direitos, consentimento e ausência de segredos; referências externas podem ser armazenadas sem copiar seu conteúdo. O dataset tem licença explícita por componente, política de contribuições e retirada de acesso quando necessária.

## 4. Arquitetura de execução

- **Cliente local:** `pip install nablamath` no futuro, CLI `nabla`, banco SQLite, fila local e configuração; inicialização no Windows por `setup.ps1` ou `setup.cmd`, com macOS/Linux por `setup.sh`. Instalador verifica versões e explica dependências opcionais (Lean/Lake, compilador LaTeX, GPU, Blender). Não promete instalar tudo silenciosamente nem elevar privilégios. Instalação básica funciona sem serviços remotos.
- **Motor científico:** API Python canônica, expressão com domínio e unidade, adaptadores para bibliotecas maduras, passos auditáveis, relatório e render científico. Arquivo único opcional gerado a partir da API canônica depois de teste de equivalência.
- **Lean:** projeto Lake com versão fixada e Mathlib compatível, tradutor bidirecional em subconjunto explícito, arquivos de prova e verificação independente; nunca interpretar simples compilação como validação de uma teoria física.
- **Contribuição distribuída:** serviço de coordenação com tarefas pequenas, leases, cotas, resultados endereçados por conteúdo, reexecução por outro nó, reputação baseada em evidência, controle de abuso e cancelamento. Usar HTTP/eventos e armazenamento apropriados; reservar computação voluntária para cargas seguras e com orçamento explícito.
- **Registro compartilhado:** log de eventos encadeados por hash ou árvore de Merkle, snapshots assinados e verificáveis; contas e atribuição de contribuições. Uma blockchain pública com consenso próprio, token ou mineração **não é requisito**. Avaliar ancoragem opcional em rede existente somente se houver uma necessidade demonstrada de auditabilidade entre partes que não confiam umas nas outras. Hashes provam integridade histórica, não a veracidade científica.
- **Publicação:** GitHub Pages hospeda site estático e visualizações de snapshots; métricas quase em tempo real exigem uma API/serviço separado e cache. Hugging Face hospeda snapshots versionados de datasets após curadoria; um job de publicação diário só roda se houver lote novo aprovado e autenticação configurada.
- **Outras linguagens:** primeiro estabilizar protocolo de dados/API; depois SDKs e bindings em Rust, C e C++. Não duplicar motores matemáticos sem justificativa.

## 5. Inventário de arquivos e pastas planejados

Convenção: cada linha é **caminho futuro** e conteúdo/contrato esperado. Acrescentar arquivos para cada novo domínio por uma proposta de arquitetura; milhares de arquivos serão definidos quando seus contratos forem conhecidos. Manter `current scripts/` e `legacy/` como referência, escolhendo implementações por teste e auditoria, não copiando tudo para `src/`.

### Fundação, instalação e governança — F0

| Caminho | Deve conter |
|---|---|
| `pyproject.toml` | Metadados, versão Python suportada, dependências mínimas, extras (`lean`, `latex`, `viz`, `orbital`, `server`, `dev`), entrada CLI e build. |
| `uv.lock` ou equivalente | Lock reproduzível da instalação de desenvolvimento; escolher uma ferramenta e documentar o processo de atualização. |
| `setup.ps1` | Bootstrap Windows: verificar Python, ambiente isolado, instalar pacote e executar diagnóstico; parâmetros explícitos para opcionais. |
| `setup.cmd` | Chamada curta ao script PowerShell com saída legível no CMD. |
| `setup.sh` | Bootstrap POSIX equivalente, sem uso implícito de privilégios elevados. |
| `LICENSE` | Licença do código escolhida pelo mantenedor; distinguir licença dos datasets e de ativos de terceiros. |
| `CONTRIBUTING.md` | Como propor problemas, código, provas, datasets e revisão científica. |
| `CODE_OF_CONDUCT.md` | Regras da comunidade e canal de moderação. |
| `SECURITY.md` | Relato de vulnerabilidades, execução de código de agentes e política de divulgação. |
| `CITATION.cff` | Citação de software, autores e versões. |
| `.gitignore` | Artefatos de build, ambientes, bancos locais, credenciais, renders e datasets intermediários. |
| `.github/ISSUE_TEMPLATE/feature.yml` | Escopo, evidências, dependências e critério de aceite por recurso. |
| `.github/ISSUE_TEMPLATE/science.yml` | Hipóteses, unidades, validação de modelo e referências por problema científico. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Checklist de testes, licenças, proveniência e mudança de contrato. |
| `docs/ROADMAP_GLOBAL_RESEARCH.md` | Este roteiro, mantenedor da ordem, estado e contratos. |
| `docs/DECISIONS/README.md` | Índice de decisões de arquitetura com alternativas e justificativas. |
| `docs/COMPATIBILITY.md` | Matriz de Python, SO, Lean, Mathlib, LaTeX e adaptadores por release. |
| `docs/THREAT_MODEL.md` | Ameaças dos nós externos, código não confiável, dados maliciosos, chaves e publicação. |

### Núcleo Python e dados locais — F1

| Caminho | Deve conter |
|---|---|
| `src/nablamath/__init__.py` | API pública curta e versão do pacote. |
| `src/nablamath/cli.py` | Comandos `doctor`, `init`, `run`, `verify`, `report`, `dataset`, `contribute` e ajuda; implementar gradualmente. |
| `src/nablamath/config.py` | Configuração local tipada, defaults seguros e caminhos de projeto. |
| `src/nablamath/errors.py` | Erros tipados com causa e identificador de etapa. |
| `src/nablamath/schema/problem.py` | Problema, objetivo, premissas, domínio e referências. |
| `src/nablamath/schema/expression.py` | AST, tipos numéricos, domínio, forma exata/aproximada e serialização. |
| `src/nablamath/schema/units.py` | Dimensões, sistemas de unidades e conversões explícitas. |
| `src/nablamath/schema/step.py` | Transformação, regra, pré-condições, entrada/saída e obrigação de prova. |
| `src/nablamath/schema/evidence.py` | Estados e evidências formais, numéricas, experimentais e de revisão. |
| `src/nablamath/schema/artifact.py` | Conteúdo, derivação, origem, licenças, versões e anexos. |
| `src/nablamath/schema/experiment.py` | Experimento, métrica, orçamento, semente, amostragem e resultado. |
| `src/nablamath/schema/version.py` | Versão de schema, compatibilidade e políticas de migração. |
| `src/nablamath/symbolic/parser.py` | Parser seguro para subconjunto documentado, sem `eval`. |
| `src/nablamath/symbolic/rules.py` | Regras algébricas com condições de validade e identificadores estáveis. |
| `src/nablamath/symbolic/derive.py` | Derivação simbólica e registro de passos verificáveis. |
| `src/nablamath/symbolic/assumptions.py` | Propagação, conflitos e lacunas de hipóteses. |
| `src/nablamath/numeric/evaluate.py` | Avaliação com precisão, domínios, tolerâncias e erros explícitos. |
| `src/nablamath/numeric/linear.py` | Álgebra linear apoiada em backend existente, com proveniência. |
| `src/nablamath/numeric/ode.py` | Interface de EDOs, eventos e validação de unidades. |
| `src/nablamath/autodiff/api.py` | JVP/VJP e compatibilidade com backends; gradiente checado contra referências. |
| `src/nablamath/pipeline/engine.py` | DAG de tarefas determinístico/reexecutável e estados de execução. |
| `src/nablamath/pipeline/cache.py` | Cache por conteúdo, parâmetros, ambiente e versão de ferramenta. |
| `src/nablamath/pipeline/provenance.py` | Encadeamento de resultados, hashes canônicos e fontes. |
| `src/nablamath/store/sqlite.py` | Persistência local, índices, transações e migrações. |
| `src/nablamath/store/blobs.py` | Arquivos grandes endereçados por hash, verificação e coleta de lixo segura. |
| `src/nablamath/store/migrations/README.md` | Regras para migrar schema sem perder histórico. |
| `src/nablamath/adapters/sympy.py` | Conversões explícitas para/de SymPy e testes de semântica. |
| `src/nablamath/adapters/numpy.py` | Arrays e precisão, metadados de forma e unidade. |
| `src/nablamath/adapters/scipy.py` | Solvers e proveniência de versão/tolerância. |
| `src/nablamath/adapters/registry.py` | Capacidades declaradas e dependências opcionais dos adaptadores. |
| `tests/unit/test_domain_rules.py` | Regressões para zero, singularidades, raízes, ramos e hipóteses. |
| `tests/unit/test_units.py` | Consistência dimensional e conversões. |
| `tests/unit/test_schema_roundtrip.py` | Serialização e migração sem perda semântica. |
| `tests/integration/test_cli_local.py` | Instalação, início, execução e consulta sem servidor ou IA. |
| `examples/first_problem.py` | Primeiro caso manual reproduzível, com documentação em português. |

### Lean, LaTeX, visualização e domínios — F2/F3

| Caminho | Deve conter |
|---|---|
| `lean/lakefile.lean` | Dependências Lean/Mathlib fixadas e targets de verificação. |
| `lean/lean-toolchain` | Versão específica do Lean para build reprodutível. |
| `lean/NablaMath/Prelude.lean` | Definições mínimas compartilhadas e semântica das expressões traduzidas. |
| `lean/NablaMath/Algebra/Rules.lean` | Lemas para subconjunto de regras demonstradas. |
| `lean/NablaMath/Examples/FirstProblem.lean` | Primeiro exemplo com proposição humana comparada à formal. |
| `src/nablamath/formal/translate.py` | Tradução explícita AST/hipóteses → enunciado Lean; rejeição de casos não suportados. |
| `src/nablamath/formal/check.py` | Invocação isolada, timeout, versões, logs e validação de saída. |
| `src/nablamath/formal/obligations.py` | Fila de objetivos não provados, contraexemplos e status. |
| `src/nablamath/formal/review.py` | Revisão da correspondência entre enunciado original e formalizado. |
| `tests/integration/test_lean_bridge.py` | Provas positivas/negativas e falhas de tradução ou de hipótese. |
| `src/nablamath/reports/model.py` | Relatório a partir do registro de passos e fontes, sem texto repetido artificial. |
| `src/nablamath/reports/latex.py` | Emissão `.tex`, equações numeradas, referências e manifesto. |
| `src/nablamath/reports/compile.py` | Compilação opcional, logs e verificação de saída real. |
| `src/nablamath/viz/spec.py` | Dados, cores, eixos, unidade, origem e rótulo de proxy. |
| `src/nablamath/viz/plot.py` | Gráficos 2D/3D diagnósticos com exportação de dados. |
| `src/nablamath/viz/render.py` | Interface de renderização e parâmetros de reprodução. |
| `src/nablamath/adapters/blender.py` | Exportador opcional, sem alegar render validado antes de executar Blender. |
| `src/nablamath/physics/orbital/state.py` | Estado, referencial, unidades e hipóteses do veículo. |
| `src/nablamath/physics/orbital/dynamics.py` | Órbitas de referência, integração e invariantes de dois corpos. |
| `src/nablamath/physics/orbital/validation.py` | Casos analíticos, erros, validade física e alertas. |
| `src/nablamath/physics/fluids/model.py` | Interfaces para modelos de fluidos com regime/condições de contorno explícitos. |
| `src/nablamath/physics/fluids/validation.py` | Benchmarks e observações, separados de prova formal das equações. |
| `tests/science/test_orbital_reference.py` | Comparação com soluções analíticas e unidades SI. |
| `tests/science/test_fluids_reference.py` | Casos controlados e tolerâncias, quando o módulo existir. |
| `examples/orbit_report.py` | Problema completo com resultados, figura, `.tex` e limites do modelo. |

### Agentes, dados sintéticos e avaliação — F3/F4

| Caminho | Deve conter |
|---|---|
| `src/nablamath/agents/protocol.py` | Ferramentas tipadas para propor, executar, criticar e justificar. |
| `src/nablamath/agents/budget.py` | Cotas de tempo, tokens, CPU/GPU, armazenamento e cancelamento. |
| `src/nablamath/agents/sandbox.py` | Isolamento de código gerado e restrições de recursos; falha fechada. |
| `src/nablamath/agents/trajectory.py` | Passos, prompts permitidos, decisões, falhas e recuperação. |
| `src/nablamath/agents/selector.py` | Seleção de problemas por novidade, relevância e orçamento. |
| `src/nablamath/dataset/schema.py` | Registro de treino e documentação da semântica das colunas. |
| `src/nablamath/dataset/deduplicate.py` | Canonização e detecção de variações triviais/vazamento. |
| `src/nablamath/dataset/quality.py` | Utilidade, correção, diversidade, revisão e quarentena. |
| `src/nablamath/dataset/splits.py` | Separação temporal e por famílias; benchmarks não usados no treino. |
| `src/nablamath/dataset/export.py` | Shards Parquet, fontes e manifesto de snapshot. |
| `src/nablamath/dataset/licenses.py` | Elegibilidade, atribuição e exclusões de redistribuição. |
| `src/nablamath/dataset/cards.py` | Dataset card com escopo, origens, limitações e uso. |
| `benchmarks/baselines/README.md` | Baselines de resolução, retenção, generalização e custo. |
| `benchmarks/tasks/README.md` | Conjuntos privados/temporais e regras de avaliação sem vazamento. |
| `tests/integration/test_dataset_pipeline.py` | Integridade dos shards, licenças, estados e deduplicação. |
| `tests/integration/test_agent_limits.py` | Cotas, isolamento, cancelamento e nenhum acesso indevido. |

### Rede, site e publicação — F4/F5

| Caminho | Deve conter |
|---|---|
| `services/coordinator/app.py` | API autenticada de tarefas, contribuições e consulta. |
| `services/coordinator/auth.py` | Identidade, chaves de participante e permissões. |
| `services/coordinator/scheduler.py` | Priorização, leases, reatribuição, cotas e proteção contra spam. |
| `services/coordinator/review.py` | Replicação de verificação, divergência e revisão humana. |
| `services/coordinator/events.py` | Log append-only, retificações e assinaturas. |
| `services/coordinator/snapshots.py` | Manifestos, Merkle root, auditoria e exportação pública. |
| `services/coordinator/metrics.py` | Métricas definidas: participantes ativos únicos, tarefas e qualidade, com janela temporal. |
| `services/coordinator/db/README.md` | Schema, migração, backups, retenção e restauração. |
| `services/worker/agent.py` | Cliente voluntário com opt-in, limites, execução isolada e entrega assinada. |
| `services/worker/checkpoint.py` | Continuação e sincronização sem duplicar trabalho. |
| `services/publisher/huggingface.py` | Publicador de lotes aprovados, idempotente e versionado; nenhuma credencial no código. |
| `services/publisher/manifest.py` | Receipts, hashes e auditoria da publicação diária. |
| `website/package.json` | Build de site estático com versões travadas. |
| `website/src/index.*` | Página inicial, instalação, visão e estado real dos módulos. |
| `website/src/roadmap.*` | Etapas, progresso verificável e links para issues/PRs. |
| `website/src/explorer.*` | Pesquisa por problema, prova, evidência e proveniência. |
| `website/src/community.*` | Participantes opt-in e métricas com definições transparentes. |
| `website/src/data.*` | Fonte de métricas/snapshots sem expor dados privados. |
| `website/public/.nojekyll` | Build estático compatível com GitHub Pages. |
| `.github/workflows/ci.yml` | Lint, tipos, testes reais do pacote e verificação de compatibilidade. |
| `.github/workflows/lean.yml` | Compilação e checagem formal com versões fixadas. |
| `.github/workflows/pages.yml` | Build/deploy do site somente após testes. |
| `.github/workflows/dataset-publish.yml` | Job diário condicionado à curadoria, novo lote e credencial segura. |
| `tests/integration/test_coordinator.py` | Corridas, leases, autenticação, abuso e revalidação externa. |
| `tests/integration/test_publisher.py` | Idempotência, erro de rede, manifesto e rollback por novo snapshot. |
| `docs/OPERATIONS.md` | Deploy, backups, incidentes, custos, domínio e métricas. |
| `docs/DATA_GOVERNANCE.md` | Direitos, consentimento, remoção/retratação, política global e atribuição. |

### Interoperabilidade e evolução — F5+

| Caminho | Deve conter |
|---|---|
| `protocol/schema/README.md` | Formatos estáveis, versionamento, testes de conformidade e tratamento de precisão. |
| `protocol/fixtures/README.md` | Fixtures ouro e hashes entre linguagens. |
| `sdk/rust/README.md` | Leitura/escrita do protocolo, erros e integração com Python. |
| `sdk/c/README.md` | ABI pequena e estável, ownership de memória e FFI. |
| `sdk/cpp/README.md` | Wrapper C++ sobre ABI/protocolo com testes. |
| `tests/interop/README.md` | Testes cruzados de precisão, serialização e identidade dos resultados. |
| `tools/singlefile/README.md` | Gerador de distribuição opcional derivada dos módulos e teste de equivalência. |

Arquivos `__init__.py`, tipos, testes de cada regra/modelo, documentação de novas áreas e scripts de migração serão adicionados junto com seus módulos, sem criar pastas vazias apenas para completar a tabela.

## 6. Checklist de entrega por fase

### Incremento em revisão — 24/09/2026

Novo recorte: contratos de problemas/unidades/evidências, solver linear racional, RK4, diferenciação direta escalar, solução analítica de fluxo laminar em tubo, coordenação SQLite local com duas reexecuções, raiz Merkle, adaptadores de fração canônica C/C++/Rust e guia de leitura. Executar `python tools/roadmap_status.py` para ver caminhos faltantes; a presença dos arquivos não basta para concluir as fases.

- [x] Executor local: expressões racionais, SQLite, reexecução e fonte LaTeX.
- [x] Caso orbital analítico: vis-viva, período, condições SI, checagens independentes de conservação em testes.
- [x] Diagrama SVG local em escala da órbita ideal, com foco explícito e texto de acessibilidade.
- [x] Gerador Lean de proposições de instâncias racionais e lemas estáticos; CI Lean/Mathlib compilou a biblioteca e verificou duas instâncias racionais (execução `36010666417`).
- [x] Curadoria local JSONL: reexecução, declaração explícita de licença/procedência, divisões determinísticas por expressão.
- [x] Troca manual de snapshots entre dois bancos locais: manifesto SHA-256, reexecução, importação transacional e idempotente.
- [ ] Prova formal simbólica de cada regra com hipóteses, revisão humana de tradução e registro persistente do resultado formal.
- [ ] Comparação orbital com fonte externa, unidade física automática, modelos perturbados, CFD validado e visualização auditável.
- [x] Implementar publicador opt-in com auditoria, aprovação vinculada ao hash e workflow diário condicionado à configuração.
- [ ] Publicação real sob conta escolhida, API multiusuário, sincronização e reprodução por máquinas independentes.

Nenhuma das fases F1–F6 completas abaixo decorre apenas destes incrementos. A ação Lean no GitHub já compilou o exemplo; isso prova duas **instâncias numéricas**, sem estabelecer uma identidade gerada universal nem verificar modelos físicos.

- [ ] **F0 — especificação:** definir licenças e governança, escolher formatos e versões, aprovar contratos de evidência e ameaças; manter README honesto sobre o status.
- [ ] **F1 — produto local:** `pip install`, bootstrap Windows, `doctor`, CLI e banco local; primeiro problema reproduzível de ponta a ponta sem IA.
- [ ] **F2 — rigor e comunicação:** passos condicionais, Lean para um subconjunto verificável, LaTeX compilável e visualização com proveniência; teste humano da tradução formal.
- [ ] **F3 — ciência e agentes:** orbital validado em referências, fluidos por escopo, agentes limitados, benchmarks e trajetória local com falhas preservadas.
- [ ] **F4 — dataset e site:** export Parquet e card, site estático no GitHub Pages com snapshots reais; publicação Hugging Face somente após validação e autorização da conta.
- [ ] **F5 — computação global:** serviço de coordenação, clientes voluntários, verificação redundante, identidade/atribuição, métricas auditáveis e sincronização quase em tempo real.
- [ ] **F6 — linguagens e pesquisa avançada:** protocolo/SDKs Rust/C/C++, comparações de treinamento em dados curados, revisões científicas e novas áreas por módulos.

Em **cada fase**, um agente deve: (a) apontar os arquivos criados/alterados; (b) justificar contratos e dependências; (c) implementar o menor fluxo executável; (d) escrever testes científicos independentes; (e) rodar a suíte e registrar comandos/resultados; (f) atualizar README e esta lista; (g) identificar o que continua hipotético. Não marcar uma fase pronta com apenas arquivos criados ou páginas de marketing.

## 7. Critérios de sucesso e dependências externas

O primeiro marco demonstrável é: instalação limpa em Windows e Linux, problema criado via Python/CLI, passos verificáveis, um teorema Lean correspondente revisado, cálculo numérico com teste de referência, relatório `.tex`/PDF quando o compilador estiver presente e registro no SQLite. O marco público seguinte é: duas máquinas produzem tarefas independentes, um verificador externo reproduz os resultados, um snapshot curado é publicado no Hugging Face e o site mostra métricas obtidas desse snapshot. Novidade científica e ganhos de modelos são hipóteses a testar contra baselines, não critérios que possam ser declarados por design.

GitHub Pages hospeda conteúdo estático. Para contagem de participantes e tarefas em tempo real, será necessário operar API/banco fora do Pages ou publicar snapshots periódicos. Publicação no Hugging Face exige uma conta/organização, repositório de dataset, licença e credenciais; não há dataset público até essas dependências serem criadas e configuradas. Operar rede global envolve custos, disponibilidade, moderação e manutenção contínua. Versões, limites e custos devem ser reavaliados antes de cada implantação.
