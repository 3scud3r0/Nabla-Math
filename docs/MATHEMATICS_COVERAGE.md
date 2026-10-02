# Cobertura matemática: fronteira aberta e inventário de módulos

**Estado:** inventário arquitetural, não alegação de cobertura.  
**Princípio:** “toda a matemática” não é um escopo finito: novos teoremas, áreas e
formalizações continuam surgindo. Um arquivo existente tampouco comprova correção,
completude ou validação científica.

## Blocos implementados

- Objetos canônicos endereçados por conteúdo e armazenamento local atômico.
- Manifestos de dataset comprometidos por raiz Merkle.
- Recibos declarativos de verificação e retratações aditivas.
- Schemas públicos v1 para objetos, recibos, tarefas limitadas e linhagem de modelos.
- Regras normativas para encoding e números, acompanhadas de fixture dourada.
- Normalização Unicode NFC, rejeição de chaves JSON duplicadas e de bytes não canônicos.
- Migrações explícitas e bundles offline limitados com validação integral de IDs.
- Fragmentação e remontagem determinísticas com hashes por chunk e do conteúdo final.
- Nó estritamente offline com política local de tipos, licenças, tamanho e dependências.
- Orçamentos de CPU, memória, disco, rede e tempo que pedidos externos não ampliam.
- Pins e criação determinística de snapshots locais.
- Consentimento persistido, desativado por padrão, expiração e auditoria offline do store.
- Grafo acíclico local de ancestralidade, descendência e retratações.
- Baselines de governança da rede, modelos e resposta a incidentes.
- Diretório efêmero de peers, HTTPS obrigatório fora de loopback, TTL e capabilities.
- Rate limiting, quarentena local e replicação topológica de lotes.
- Workspace SQLite e registro de modelos endereçado por conteúdo.
- Compromissos de avaliação selada e detecção conservadora de contaminação por proveniência.
- Servidor explícito somente em loopback, autenticação por bearer token e cliente sem redirects.

Esses blocos não implementam transporte P2P, identidade, assinatura, consenso, execução
de tarefas remotas ou treinamento distribuído. Recibos registram uma alegação e sua
evidência; não transformam consenso em verdade científica.

## Arquivos e blocos de infraestrutura ainda necessários

### Protocolo e compatibilidade

- `src/nablamath/network/signatures.py`: assinatura assimétrica e rotação/revogação de chaves.
- `protocol/fixtures/cross-language/`: fixtures verificadas pelos SDKs C/C++/Rust/TypeScript.
- Assinaturas normativas dos schemas e fixtures por mantenedores.

### Nó local e execução segura

- `src/nablamath/node/identity.py`; o daemon de referência existe apenas para loopback
- Persistência transacional de pins/políticas e recuperação após falha.
- Sandbox real por processo/contêiner; o orçamento existente apenas valida limites.
- UI explícita de opt-in, pausa, remoção, bateria, energia e banda.
- Atualizações assinadas e rollback.

### Rede voluntária

- retrieval/replicação de rede completos; o transporte atual é um cliente limitado e o servidor só aceita loopback
- `src/nablamath/p2p/{moderation,reputation}.py` (rate limit e quarentena local já existem)
- `services/registry/{app,api,db,metrics}.py`
- `services/relay/{app,protocol,abuse}.py`
- `tests/network/{interop,partition,sybil,poisoning,eclipse}.py`
- NAT traversal, TLS, autenticação, proteção contra replay e operação multiusuário.

### Produção, verificação e avaliação de dados

- `src/nablamath/knowledge/{lineage,novelty,difficulty,curriculum}.py`
- `src/nablamath/verification/{independence,evidence,consensus}.py`
- `src/nablamath/evaluation/{calibration,ablation}.py`; sealed/contamination locais ainda requerem operação independente
- `src/nablamath/training/{snapshot,mixture,lineage}.py`; registry local já existe
- `benchmarks/private/README.md` e `benchmarks/contamination/`
- revisão/aprovação institucional das políticas iniciais de rede, modelos e incidentes
- Avaliadores realmente independentes, benchmarks privados e estudos de ablação.

## Recortes matemáticos implementados nesta etapa

- Lógica proposicional e semântica de primeira ordem em estruturas finitas, com termos, relações e quantificadores.
- Álgebra: grupos, anéis e corpos finitos explícitos, grupos cíclicos, anéis `ℤ/nℤ` e corpos primos.
- Teoria elementar dos números: Euclides estendido, inverso modular, primalidade por divisão
  e fatoração exata, congruências lineares e teorema chinês dos restos.
- Álgebra linear: matrizes racionais, transposição, produto, forma escalonada, posto, determinante e inversa.
- Grafos: componentes, DAGs, matching bipartido, Dijkstra racional e fluxo máximo.
- Topologia finita: axiomas, continuidade, interior, fecho, fronteira, subespaços e conexidade.
- Análise real/complexa numérica: bisseção, trapézios, Simpson, diferenças finitas, Newton, sequências, aceleração de Aitken, forma polar e raízes complexas.
- Probabilidade finita: conjuntas, marginais, independência, cadeias de Markov, Bayes exato, estatística, regressão e séries temporais descritivas.
- Combinatória enumerativa: binomiais, arranjos e números de partições.
- Polinômios univariados racionais: operações, avaliação, derivada, divisão euclidiana, MDC mônico e interpolação exata.
- Linguagens formais: autômatos finitos determinísticos totais, aceitação e alcançabilidade.
- Teoria de conjuntos finitos: conjuntos potência, produtos, relações de equivalência, injetividade e sobrejetividade.
- Sistemas dinâmicos discretos: iteração limitada e detecção exata de ciclos em estados hashable.
- Teoria dos jogos: jogos bimatriciais finitos, equilíbrios puros, soma zero e maximin puro.
- Informação: códigos binários livres de prefixo, soma de Kraft, codificação/decodificação, entropia, KL e informação mútua finitas.
- Aritmética: frações contínuas racionais, convergentes e aproximações finitas.
- Equações: integração explícita de ODEs por Euler e RK4 com limites e validação.
- Criptografia clássica pedagógica: César e Vigenère, explicitamente não modernas.
- Otimização linear 2D, controle linear discreto e fórmulas estacionárias M/M/1 e escalonamento de máquina única.
- Geometria euclidiana/convexa plana racional: distância, orientação, área, fecho convexo e pertinência.
- Teoria das categorias finitas: categorias por tabelas, categorias discretas, funtores e
  transformações naturais, objetos iniciais/terminais, isomorfismos e produtos por propriedade universal.

Esses são recortes pequenos e explícitos. Eles não tornam as áreas correspondentes
“implementadas por completo” e não substituem provas Lean ou revisão especializada.

## Domínios matemáticos ainda necessários

Cada diretório abaixo precisaria, no mínimo, de `schema.py`, `algorithms.py`,
`validation.py`, `references.py`, testes unitários, propriedades, casos negativos,
benchmarks, documentação, exemplos e — quando possível — formalização Lean. A lista é
uma taxonomia de engenharia ampla, não uma enumeração definitiva da matemática.

### Fundamentos e lógica (semântica proposicional e primeira ordem finita parcialmente implementada)

- `src/nablamath/math/logic/{propositional,first_order,higher_order,modal,temporal}.py`
- `src/nablamath/math/logic/{intuitionistic,relevance,many_valued,linear}.py`
- `src/nablamath/math/proof_theory/{sequent,natural_deduction,normalization,ordinal}.py`
- `src/nablamath/math/model_theory/{structures,compactness,types,stability}.py`
- `src/nablamath/math/computability/{machines,recursion,decidability,degrees}.py`
- `src/nablamath/math/type_theory/{dependent,inductive,homotopy,cubical}.py`
- `src/nablamath/math/set_theory/{zfc,ordinals,cardinals,forcing,large_cardinals}.py`

### Aritmética e teoria dos números (algoritmos elementares parcialmente implementados)

- `src/nablamath/math/arithmetic/{integers,rationals,continued_fractions}.py`
- `src/nablamath/math/number_theory/{elementary,analytic,algebraic,geometric}.py`
- `src/nablamath/math/number_theory/{diophantine,modular_forms,automorphic,p_adic}.py`
- `src/nablamath/math/number_theory/{elliptic_curves,l_functions,class_field}.py`

### Álgebra (grupos, anéis e corpos finitos explícitos parcialmente implementados)

- `src/nablamath/math/algebra/{groups,rings,fields,modules,ideals}.py`
- `src/nablamath/math/algebra/{lattices,semigroups,universal,homological}.py`
- `src/nablamath/math/algebra/{commutative,noncommutative,representation}.py`
- `src/nablamath/math/algebra/{lie_groups,lie_algebras,hopf,clifford}.py`
- `src/nablamath/math/algebra/{galois,groebner,computer_algebra}.py`

### Geometria e topologia (operações em topologias finitas parcialmente implementadas)

- `src/nablamath/math/geometry/{euclidean,affine,projective,convex,discrete}.py`
- `src/nablamath/math/geometry/{differential,riemannian,symplectic,contact}.py`
- `src/nablamath/math/geometry/{algebraic,arithmetic,complex,noncommutative}.py`
- `src/nablamath/math/topology/{general,algebraic,differential,geometric}.py`
- `src/nablamath/math/topology/{homotopy,homology,cohomology,knot,manifolds}.py`
- `src/nablamath/math/topology/{persistent,low_dimensional,spectral_sequences}.py`

### Análise (real/complexa numérica e sequências parcialmente implementadas)

- `src/nablamath/math/analysis/{real,complex,functional,harmonic}.py`
- `src/nablamath/math/analysis/{fourier,microlocal,convex,variational}.py`
- `src/nablamath/math/analysis/{measure,integration,distribution,operator}.py`
- `src/nablamath/math/analysis/{asymptotic,numerical,interval,nonstandard}.py`
- `src/nablamath/math/dynamical_systems/{continuous,discrete,ergodic,chaos}.py`

### Equações e sistemas físicos matemáticos (ODEs explícitas parcialmente implementadas)

- `src/nablamath/math/equations/{ode,pde,dae,integral,stochastic}.py`
- `src/nablamath/math/equations/{elliptic,parabolic,hyperbolic,conservation}.py`
- `src/nablamath/math/math_physics/{classical,quantum,relativity,statistical}.py`
- `src/nablamath/math/math_physics/{field_theory,string,integrable_systems}.py`

### Probabilidade, estatística e informação (conjuntas finitas/regressão parcialmente implementadas)

- `src/nablamath/math/probability/{foundations,processes,martingales,stochastic_calculus}.py`
- `src/nablamath/math/probability/{random_matrices,percolation,concentration}.py`
- `src/nablamath/math/statistics/{frequentist,bayesian,causal,nonparametric}.py`
- `src/nablamath/math/statistics/{multivariate,time_series,survival,spatial}.py`
- `src/nablamath/math/information/{entropy,coding,algorithmic,quantum}.py`

### Matemática discreta e computação (conjuntos finitos, grafos, fluxos e combinatória parcialmente implementados)

- `src/nablamath/math/combinatorics/{enumerative,extremal,algebraic,probabilistic}.py`
- `src/nablamath/math/combinatorics/{designs,matroids,partitions,ramsey}.py`
- `src/nablamath/math/graph_theory/{structural,spectral,random,directed,hypergraphs}.py`
- `src/nablamath/math/algorithms/{complexity,approximation,randomized,online}.py`
- `src/nablamath/math/cryptography/{classical,elliptic,lattice,post_quantum}.py`
- `src/nablamath/math/formal_languages/{grammars,semantics,rewriting}.py` (DFA total parcialmente implementado)

### Otimização, decisão e jogos (LP 2D e jogos finitos puros parcialmente implementados)

- `src/nablamath/math/optimization/{linear,integer,convex,nonconvex,global}.py`
- `src/nablamath/math/optimization/{combinatorial,stochastic,robust,multiobjective}.py`
- `src/nablamath/math/control/{linear,nonlinear,optimal,robust,distributed}.py`
- `src/nablamath/math/game_theory/{cooperative,noncooperative,evolutionary,algorithmic}.py`
- `src/nablamath/math/operations_research/{queues,scheduling,networks,inventory}.py`

### Teoria das categorias e estruturas superiores (núcleo finito parcialmente implementado)

- `src/nablamath/math/category_theory/{categories,functors,natural_transformations}.py`
- `src/nablamath/math/category_theory/{limits,adjunctions,monads,kan_extensions}.py`
- `src/nablamath/math/category_theory/{enriched,internal,monoidal,braided}.py`
- `src/nablamath/math/category_theory/{topos,sheaves,stacks,descent}.py`
- `src/nablamath/math/category_theory/{higher,infinity_categories,operads}.py`
- `src/nablamath/math/category_theory/{categorical_logic,derived,homotopical}.py`
- `lean/NablaMath/CategoryTheory/` (integração revisada com Mathlib, sem duplicá-la)

### Matemática aplicada e interdisciplinar

- `src/nablamath/math/applied/{fluids,solids,waves,electromagnetism}.py`
- `src/nablamath/math/applied/{networks,epidemiology,population,ecology}.py`
- `src/nablamath/math/applied/{economics,finance,actuarial,signal_processing}.py`
- `src/nablamath/math/applied/{imaging,inverse_problems,geoscience,climate}.py`
- `src/nablamath/math/applied/{systems_biology,neuroscience,genomics}.py`

### Metamatemática, história e pedagogia

- `src/nablamath/math/meta/{ontology,equivalence,dependency,notation}.py`
- `src/nablamath/math/meta/{difficulty,novelty,explanation,counterexamples}.py`
- `src/nablamath/math/history/{sources,attribution,timeline}.py`
- `src/nablamath/math/education/{curricula,prerequisites,misconceptions,assessment}.py`

## Critério para declarar suporte a um domínio

Um domínio só pode aparecer como suportado quando houver simultaneamente:

1. escopo matemático finito e explicitamente nomeado;
2. semântica, hipóteses, unidades e erros definidos;
3. implementação e API versionadas;
4. testes positivos, negativos, propriedades e fronteiras;
5. comparação com referência independente;
6. proveniência e licença das fixtures;
7. benchmarks sem vazamento;
8. documentação das limitações;
9. revisão especializada;
10. evidência reproduzível publicada.

Nem mesmo a soma de todos os arquivos acima cobriria “100% da matemática”. O objetivo
tecnicamente honesto é uma plataforma extensível capaz de adicionar recortes verificáveis
sem confundir existência de código com verdade matemática.
