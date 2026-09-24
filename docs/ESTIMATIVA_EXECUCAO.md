# Estimativa de execução do roteiro global

Atualizada em 24/09/2026. São **intervalos de planejamento**, não previsão de descobertas, datas de AGI ou compromisso de lançamento. Considera dois engenheiros experientes em dedicação integral, consultoria regular de especialista em Lean e física, infraestrutura modesta, revisão independente e módulos de escopo explícito. A mesma pessoa trabalhando sozinha e em tempo parcial amplia bastante os prazos.

| Marco | Entrega observável | Esforço adicional estimado | Calendário indicativo, com paralelismo |
| --- | --- | ---: | ---: |
| F0 | Decisões de licença, contribuição, matriz de compatibilidade e critérios de evidência | 1–2 pessoa-meses | 1–2 meses |
| F1 | Pacote estável, instalação Windows/Linux, API e recuperação/migração de dados | 2–5 pessoa-meses | 2–4 meses |
| F2 | Provas simbólicas de regras sob hipóteses, revisão de tradução, PDF e gráficos testados | 5–12 pessoa-meses | 4–9 meses |
| F3 | Orbital contra efemérides/referências, um módulo de fluidos delimitado, executor de agentes auditável | 8–20 pessoa-meses | 6–15 meses |
| F4 | Dataset card, licenças verificadas, avaliação de novidade/vazamento, snapshots e site público | 4–10 pessoa-meses | 4–9 meses |
| F5 | Serviço multiusuário seguro, verificação redundante, atribuição, métricas auditáveis e operação | 12–30 pessoa-meses | 9–20 meses |
| F6 | SDKs Rust/C/C++, benchmarks de treinamento e módulos científicos adicionais | 12–36 pessoa-meses por recorte | 9–24+ meses |

O total bruto é aproximadamente **44–115 pessoa-meses** para um produto de escopo delimitado; tarefas simultâneas fazem o calendário estimado de **2,5 a 5 anos** para equipe pequena de 2–4 pessoas com revisão científica. Em dedicação individual parcial, prever **5–10+ anos**. Não há um término de “toda a ciência de A a Z”: cobertura e manutenção são contínuas.

**Estado atual:** núcleo racional local, LaTeX fonte, SQLite, caso orbital analítico e SVG, duas instâncias racionais verificadas pelo Lean na CI, curadoria local e troca manual de snapshots. F0–F6 **não** estão concluídas. O início das etapas seguintes exige escolher licença do código, titulares de dados, identidade da organização Hugging Face e política de contribuição; nenhuma plataforma pública será habilitada automaticamente. A CI Lean deverá permanecer verde e a tradução matemática revisada para ampliar a cobertura.

## Portas de validação

1. **Alfa reprodutível:** instalar em Windows/Linux limpo; CI Python e Lean verde; revisar enunciados Lean gerados e exemplos de domínio.
2. **Beta científica:** comparar resultados orbitais com referência publicada e trabalhar um problema de fluidos de contorno definido, incluindo limites e unidade física.
3. **Dataset público:** revisar direito de uso e procedência; publicar card, divisões e testes de vazamento; medir ganho contra baseline independente. Volume não é métrica de valor.
4. **Rede:** dois clientes distintos recebem trabalho de um coordenador, verificam redundância, sobrevivem a quedas e atribuem crédito verificável sem executar código arbitrário.
5. **Pesquisa aberta:** comparar modelos treinados com e sem dados NablaMath; reportar inclusive resultados nulos e custos.

Resultados de matemática formal podem crescer por anos sem gerar modelos melhores; cálculos empíricos precisam de observação e limites de erro. Datas devem ser revistas após cada porta com medições de custo e disponibilidade de colaboradores.
