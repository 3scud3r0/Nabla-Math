# NablaMath: handoff para continuidade por outra IA

## Contexto, escopo e objetivo final

Construir a biblioteca NablaMath como sistema aberto, reproduzível e extensível de matemática simbólica/numerical, autodiferenciação e tensores, ML, otimização, física de voo orbital, relatórios científicos LaTeX, relatividade, calculadora passo a passo, visualização e ferramentas de pesquisa. O usuário deseja:

- **Código real, integrado, utilizável**, inclusive uma distribuição standalone maciça `.py`; modularização para manutenção sem perder empacotamento único.
- **Relatórios longos, justificados e não repetitivos**, potencialmente centenas de páginas somente quando a análise exige; derivações de cada passo, unidades, hipóteses, valores substituídos e resultados rastreáveis; sumário, equações numeradas, referências, tabelas, figuras, apêndices e fonte `.tex`. Compilar por LaTeX real sempre que disponível.
- **Módulo de relatividade** cobrindo relatividade especial e geral, até GR tensorial com derivação e exemplos; não limitar a plot de fator de Lorentz ou preenchimento de páginas.
- **Calculadora exaustiva** com parse seguro, AST, simplificação, execução de regras e justificativa para álgebra, derivadas, integrais (quando suportadas), matrizes, propagação de incerteza, verificação substitutiva, domínio e hipóteses.
- **Motor orbital** com configuração integral do usuário como código, órbita, deorbit, reentrada, cargas térmicas/aerodinâmicas, plasma/telecom proxy com limites, captura terminal como evento dinâmico, figuras 2D/3D, vídeo e relatório extensivo. Nunca apresentar surrogate como CFD, telemetria validada ou laudo de engenharia.
- **Render 3 vias:** nativo Python, web interativo e exportador Blender opcional; qualidade cinematográfica desejada, sem reivindicar Nanite, Blender completo ou path tracing físico sem implementação e testes; uso alvo em PC Windows RTX 4060 8 GB/16 GB RAM.

## Materiais mais relevantes no acervo

**Preservar as versões de referência.** O PDF `archive/artifacts/asteria1_extreme_orbital_report.pdf` e o PDF `archive/artifacts/nablamath_v03_extreme_latex_report.pdf` são referência do usuário para aparência, estrutura e densidade de derivação. O usuário rejeitou versões posteriores que repetiam parágrafos, inseriam fórmulas como texto pobre e alegavam um nível profissional sem sustentação.

**Base matemática modular:** `archive/artifacts/nablamath/` e `archive/artifacts/nablamath_v03_work/`. Procure `core.py`, `algebra.py`, `autodiff_tensor.py`, `optimize.py`, `plotting.py`, `reports.py`, `latex_report.py`, `viz_enterprise.py`, `tests/`. Algumas árvores são cópias históricas; compare SHA antes de mesclar.

**Orbital detalhado:** `archive/artifacts/nablamath_v04_work/nablamath/orbital.py` (~113 KB, mais amplo do que o orbital compacto do all-in-one). Inclui modelos, otimização surrogate, visualização, geração de vídeo e LaTeX. A física exige auditoria dimensional e de consistência.

**Standalone multímódulos:** `archive/artifacts/NablaMath_All_Modules_LaTeX_Professional.py` (~49,5 KB). Tem classes `LatexDocument`, `ExhaustiveCalculatorModule`, `RelativityModule`, `OrbitalModule`, `NablaMathProfessionalAllModules`. CLI gera 3 relatórios e PDF combinado. **Não confundir alvo de páginas com profundidade real**: há funções `_append_*_ledger` que precisam auditoria contra repetição e conteúdo artificial.

**Render:** `archive/artifacts/nablarender_v07/nablarender/` — `core/bvh.py`, `core/meshlet.py`, `native/pathtracer.py`, `native/renderer.py`, `web/web_renderer.py`, `blender/export_blender.py`, `report/pro_report.py`; há saída visual, mas não evidência de renderer competitivo com Unreal Nanite/Cycles.

**LaTeX original:** `archive/artifacts/nablamath_v03_work/nablamath/latex_report.py`, `.tex` em `outputs_v03_pdf/`; comparar com PDF para recuperar o padrão visual e as derivações. `archive/artifacts/nabla_modules_test/` inclui fontes de relatórios de relatividade, orbital e calculadora; `nabla_modules_pro/combined/` inclui PDF de 185 páginas, que sozinho **não prova 185 páginas de conteúdo único**.

## Falhas relatadas pelo usuário — critérios não negociáveis

1. Links de sandbox de sessões anteriores expiraram; só divulgar links realmente presentes/verificados na sessão atual.
2. Vídeos feitos com Matplotlib pareceram amadores; não chamá-los cinematográficos.
3. PDFs extensos com texto repetido e matemática pobre foram rejeitados; cortar `pages_target` como preenchimento, priorizar conteúdo técnico genuíno e evidências.
4. `pdflatex` gera equações numeradas de verdade; PNG de Matplotlib para equação é fallback, não equivalente a pipeline acadêmico LaTeX.
5. Um `.py` compacto que só reimplementa simplificações **não** é a biblioteca inteira: comparar APIs, testes, features e equivalência do output. Gerar *single-file* a partir da árvore modular.
6. Arquivos supostamente gerados podem faltar. O manifesto marca **somente os itens efetivamente recuperados**, não promessas anteriores.
7. Alguns valores publicados em exemplo Asteria-1, como fluxo de calor `1.318e10 W/m²` e `4200 K` repetidos, demandam revisão: possível erro de fator no Sutton–Graves e saturação artificial de temperatura; pressão isentrópica de estagnação não é aplicável diretamente ao escoamento hipersônico com choque; plasma/X-ray proxy não são sensores físicos. Ver `ARCHITECTURE_AND_ACCEPTANCE.md`.

## Primeiras tarefas concretas

A. Reconstituir mapa de versões por SHA-256 e árvore AST; selecionar implementações canônicas por testes, não por número da versão.
B. Configurar pyproject, dependências opcionais, `pytest`, typing e CLI modular; testes de regressão para operações básicas e soluções analíticas.
C. Refazer gerador LaTeX real com modelos de documentos, registro de equações + proveniência, tabela dimensional e suporte a anexar derivação sem repetição. Testar o PDF via extração/visualização página a página.
D. Implementar cálculo passo a passo com árvore de transformações: cada passo tem regra, expressão de entrada, expressão de saída, condições de validade e check simbólico ou numérico. Casos impossíveis devem declarar limites.
E. Relatividade especial: postulados, Lorentz, intervalo, composição velocidades, quatro-vetores, energia-momento, exemplos. GR: variedades, tensores, símbolos de Christoffel, Riemann, Ricci, escalar R, Einstein, Schwarzschild, geodésicas e testes numéricos. Nada de fingir derivação geral completa por páginas de ledger.
F. Orbital: unidades SI e casos de validação (vis-viva, 2 corpos, energia/h, deorbit, atmosfera e aquecimento); fechamento de massa/energia; restrições de solo/captura. Destacar não certificação.
G. Visualizar por tiers: Matplotlib diagnóstico; WebGL/WebGPU para inspeção; offline CPU ray tracer real testado; Blender/Cycles export e render somente quando disponível. Comparar renders com golden images e métricas de tempo/memória.
H. CI GitHub para compilação/import/tests; não executar simulações pesadas nem render 4K em cada PR.

## O que o acervo não contém

Não foi possível recuperar transcrição integral literal nem uma cópia independente do PDF de relatividade com 117 páginas prometidas. O PDF separado em `nabla_modules_test/relativity/` tem 18 páginas; combinado em `nabla_modules_pro/combined/` tem 185 páginas. Ausência de MP4 no ZIP de 177 itens. Não inventar arquivos para completar a promessa.

## Requisito de transparência para outra IA

Separar sempre: **[código implementado]**, **[teste executado]**, **[modelo aproximado]**, **[intenção de projeto]**. Assinalar todas as dependências externas. Relatório de centenas de páginas é consequência de centenas de passos matemáticos distintos, não de repetição automática. Nenhum número deve ser qualificado como resultado de missão real sem fonte/validação.