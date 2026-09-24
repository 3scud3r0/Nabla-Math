# NablaMath — descrição do projeto e visão de longo prazo

> **Documento publicado para orientar implementadores e agentes de IA.** A visão completa e o anexo original integral de 4.905 linhas foram preparados em um arquivo local homônimo, `description.md`. Esta versão publicada no GitHub resume fielmente o anexo, mas **não contém ainda sua transcrição literal integral**: para preservar os bytes do texto fornecido, substitua este arquivo pela versão completa entregue nesta conversa. Não declarar que a transcrição integral está no repositório antes de verificar o upload.

## Definição

O **NablaMath** pretende ser um ambiente de matemática computacional, modelagem física, IA e pesquisa científica que integra, sob a **mesma definição semântica do problema**, matemática simbólica e numérica, autodiferenciação, otimização, simulação, aprendizado de máquina, visualização científica, provas e publicação acadêmica em LaTeX. Deve conectar **formular → derivar → calcular → testar → visualizar → documentar → comparar → refinar**, sem perder as hipóteses, unidades, transformações e origens de cada resultado.

O usuário quer uma biblioteca modular sustentável **e uma distribuição gerada automaticamente em um único `.py` massivo** contendo os módulos canônicos, para uso manual em Windows (referência de hardware RTX 4060 8 GB / 16 GB RAM). Não manter duas implementações independentes divergentes.

## Por que pode ser transformador

O diferencial pretendido é a **rastreabilidade matemática ponta a ponta**. Em um fluxo científico comum a equação é definida no notebook, calculada numa ferramenta, representada em outra e redigida manualmente num PDF. O NablaMath deseja um núcleo compartilhado para expressar o problema, acompanhar cada transformação, identificar limites de validade, comparar soluções simbólicas e numéricas e produzir imagens e publicações reproduzíveis. Assim alunos, engenheiros, pesquisadores e outras IAs poderão inspecionar de onde vem cada número ou fórmula e contestá-los. Trata-se de uma **meta e hipótese de valor**, não de desempenho ou novidade cientificamente demonstrados.

## A visão original anexada — catálogo de capacidades

O texto original, escrito antes da consolidação do nome NablaMath, utiliza também os nomes **AxiomMath**, **AxiomOS** e `axiomos`. São nomes históricos/aspiracionais e **não mudam** o nome canônico do repositório. Ele descreve a ambição de um “Sistema Operacional Matemático-Computacional para Pesquisa, IA e Descoberta”.

Os conceitos principais são:

- **`MathematicalEntity` / `MathObject` com capacidades:** números, símbolos, expressões, equações, vetores, matrizes, tensores, funções, operadores, variedades, distribuições, sistemas dinâmicos, problemas de otimização, provas, experimentos, hipóteses e conjecturas. Um objeto anuncia se suporta cálculo simbólico, numérico, visualização, diferenciação, demonstração e compilação.
- **Múltiplas representações do mesmo objeto:** AST, expressão simbólica, grafo computacional, implementação Python/NumPy, eventual backend GPU, LaTeX, objeto de prova e objeto plotável; *nenhuma representação é soberana*.
- **Matemática extensa:** aritmética exata, álgebra, cálculo, análise vetorial, álgebra linear e abstrata, topologia, geometria diferencial/riemanniana, análise funcional, EDOs/EDPs, probabilidade, processos estocásticos, teoria da informação, lógica, métodos numéricos, intervalos e incerteza.
- **Núcleo simbólico com e-graphs:** manter formas matematicamente equivalentes e escolher a forma apropriada para resolver, diferenciar, provar, avaliar numericamente ou gerar código; checar domínios e estabilidade numérica.
- **Tensores e autodiff:** eixos nomeados, grafo computacional, forward/reverse mode, Jacobianos, Hessianas, JVP/VJP, derivação implícita e visualização de backpropagation.
- **Otimização e experimentação:** métodos locais/globais/restritos/multiobjetivos, baselines, métricas, memória de experimentos, AutoML e autoaperfeiçoamento recursivo sob orçamento, testes repetidos e checagem estatística.
- **Machine learning didático e eficiente:** do algoritmo “from scratch” às arquiteturas modernas, com gradientes, atenção, representações, generalização, perfis de memória e diagnósticos explicáveis.
- **Visualização científica:** funções, contornos, campos, curvas, variedades, malhas, fluxos, paisagens de perda, treinamento, trajetórias, animações e modos 2D/3D com legendas LaTeX.
- **Provas, descoberta, compilação:** formulação de conjecturas, busca de contraexemplos, regressão simbólica, análise dimensional, integração futura com Lean/Coq/SMT e backends de compilação, cada um somente anunciado como implementado após validação.
- **`Problem`, `MathPipeline`, `SolutionBundle`, `research_mode`:** um problema gera, quando cabível, solução exata e numérica, demonstração ou status de evidência, verificações, gráficos, código, limitações e relatório.

## Continuidade no domínio científico

Três módulos prioritários vindos da conversa são **relatividade especial/geral com derivações**, **missão orbital/reentrada com verificação física** e **calculadora exaustiva passo a passo**. O motor genérico de relatório deve aceitar novos módulos capazes de centenas de páginas de conteúdo genuinamente distinto, **sem repetir texto apenas para cumprir contagem**.

O PDF Asteria-1 e o relatório simbólico v0.3 são referências da intenção de diagramação e rastreabilidade (capa, sumário, input completo, equações LaTeX numeradas, derivações, tabelas, figuras, código e metadados), **não certificados da precisão dos números neles exibidos**. É indispensável manter o `.tex` real e produzir PDF compilado pelo mecanismo LaTeX. Uma renderização em imagem das fórmulas não substitui automaticamente um relatório LaTeX nativo.

Para renderização, separar gráficos científicos, visualizações de proxies térmicos/IR/raios X/plasma, rasterização, reflexão por ray tracing demonstrável, e efeitos físicos validados. Não chamar simulação analítica surrogate de CFD, pseudo-IR de sensor, ou meshlet-inspired de Nanite completo. Blender é opcional para exportação; o fluxo nativo deve funcionar sem instalar Blender.

## Requisitos não negociáveis

1. Não confundir protótipo e API aspiracional com capacidade testada.
2. Cada afirmação quantitativa deve ter domínio, unidade, hipótese, cálculo, dados e limite de erro quando aplicável.
3. Distinguir prova, evidência numérica, conjectura, modelo proxy e suposição.
4. Não fabricar números, testes passados, imagens, PDFs, vídeos ou links.
5. As saídas longas devem ser obtidas por derivação e documentação real — nunca por preenchimento.
6. As ações de autoaperfeiçoamento precisam de reprodutibilidade, orçamento, sementes, baselines, detecção de overfitting e autorização humana quando alteram artefatos.
7. Manter a suíte de testes e o build de `.py` standalone derivado dos módulos canônicos.

## Documentos para uma outra IA

- [Visão e handoff](docs/AI_HANDOFF.md)
- [Arquitetura-alvo e critérios de aceitação](docs/ARCHITECTURE_AND_ACCEPTANCE.md)
- [Histórico recuperável da conversa](docs/CONVERSATION_FOR_NEXT_AI.md)
- [Índice dos 177 artefatos históricos](docs/CONTENT_INDEX.md)
- [Estado real da migração](docs/MIGRATION_STATUS.md)
- [Importação dos binários restantes](docs/UPLOAD_REMAINING_ARCHIVE.md)

**Aviso de integridade:** o arquivo completo `description.md` gerado nesta conversa contém o texto anexado integral. A versão no GitHub precisa ser substituída por aquela cópia para registrar literalmente todas as 4.905 linhas originais.
