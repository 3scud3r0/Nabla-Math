# Contribuir com NablaMath

Comece por [roteiro e critérios de aceite](docs/ROADMAP_GLOBAL_RESEARCH.md). Desenvolva uma alteração pequena com hipótese explícita, domínio de validade, unidade quando física, teste contra fonte independente e documentação de limites. Execute `python -m pip install -e .` e `python -m unittest discover -s tests -v`; para Lean, `cd lean && lake update && lake exe cache get && lake build`.

Para proposições Lean, deixe claros axiomas e hipóteses; nunca use `sorry`, `admit` ou axiomas novos para declarar uma prova pronta. Compare o enunciado formal com o problema original antes de interpretá-lo. Para dados, mantenha origem, licença, divisões e versão; não envie chaves, prompts privados nem dados de terceiros sem direito de uso. Resultados negativos e falhas são contribuições úteis.

As licenças do código e de uma eventual coleção pública ainda exigem decisão do mantenedor. Antes de incorporar contribuição de terceiros ou publicar dataset, a licença e a política de contribuição devem estar explícitas. PRs podem discutir arquitetura e testes enquanto essa decisão está pendente.
