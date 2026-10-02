# Laboratório autônomo limitado

O pacote `nablamath.singularity` implementa a arquitetura proposta na conversa
como um **orquestrador de pesquisa declarativo e limitado**, não como uma alegação
de AGI, singularidade ou descoberta científica autônoma.

## Fluxo implementado

1. `core/planner.py` valida um DAG de tarefas e rejeita ciclos.
2. Agentes especializados produzem propostas imutáveis; não recebem ferramentas.
3. O crítico agrega riscos e o avaliador não promove alegações automaticamente.
4. `core/memory.py` guarda registros endereçados por conteúdo com linhagem válida.
5. Experimentos possuem protocolo, seed e métricas pré-declaradas.
6. O modelo de si só declara uma capacidade após quantidade e taxa mínimas de
   avaliações; ausência de evidência continua sendo ausência de capacidade.
7. Código sugerido é somente uma especificação de patch. A configuração recusa
   habilitar execução de código gerado.

Execute uma demonstração offline com:

```bash
nabla-lab "verificar uma identidade racional"
```

## Aceleração

`nablamath.gpu` contém contratos verificáveis para buffers residentes, redução
modular usada por F4, topologia compactada de e-graphs, MCTS em lotes e guia linear
INT8. Todos possuem referência CPU determinística. Um resultado só é rotulado como
acelerado quando um backend externo declara `accelerated=True`, e a redução modular
de um backend é comparada com o oráculo exato antes de ser aceita.

Esses componentes **não são kernels CUDA/Triton** e não prometem 100% de utilização
da GPU. Para isso ainda é necessário fornecer um backend específico, medir hardware
real, validar equivalência e publicar benchmarks. O nome histórico
`cuda_f4_reduction.py` representa o ponto de integração proposto, não evidência de
que CUDA esteja instalado ou executado.

## Limites

- Não pesquisa a internet.
- Não executa código produzido por agentes.
- HMAC autentica uma mensagem entre partes que já compartilham segredo; não prova
  independência de workers nem validade científica.
- MCTS aumenta throughput de avaliação, mas não remove complexidade exponencial.
- O guia INT8 é um modelo linear auditável, não uma “intuição” geral.
- Propostas permanecem propostas até verificação formal, numérica ou empírica
  independente apropriada.
