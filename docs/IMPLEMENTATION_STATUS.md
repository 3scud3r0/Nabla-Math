# Cobertura do inventário e limites de entrega

Auditoria automática: `python tools/roadmap_status.py`. Na revisão de 24/09/2026, **54 de 122 caminhos específicos** do inventário existem; esse número conta a presença do arquivo, **não** sua conclusão. Parte dos módulos novos tem nomes equivalentes aos do roteiro, porém fora desses 122 caminhos; a arquitetura precisa decidir se será migrada antes de chamar uma fase completa.

## Fluxos já executáveis

1. Aritmética racional exata, etapas condicionais, SQLite, JSONL e LaTeX fonte.
2. Lean/Mathlib fixados e duas instâncias racionais compiladas em CI anterior.
3. Órbita de dois corpos ideal em SI e SVG; fluxo laminar analítico em tubo com conferência por quadratura.
4. Conversões dimensionais exatas, álgebra linear racional, RK4 e JVP escalar por duais.
5. Propostas declarativas de agente com cota, trajetória de falhas e recusa de execução arbitrária.
6. Curadoria local com hash, cartão, divisão estrutural; coordenação SQLite local e raiz Merkle, sem autenticação de usuários.
7. Parser C e wrapper C++ compilados; parser Rust submetido à CI de interoperabilidade.

## Bloqueios para concluir todas as fases

- O [inventário atualizado](ROADMAP_GLOBAL_RESEARCH.md) inclui ainda CFD validado em referências externas, traduções Lean simbólicas completas, web service autenticado e resistente a fraude, publicação diária segura no Hugging Face, avaliação de treinamento e suporte geral Rust/C/C++. Requerem projeto, dados, manutenção e revisão especializada.
- O mantenedor precisa decidir a licença do código e a política de contribuição. `LICENSE` não será inventado automaticamente, pois distribuição e direitos de terceiros dependem dessa decisão.
- Credenciais, organização e aceite de publicação não existem neste repositório. Site e dataset público não foram ativados.
- O plano original estima **44–115 pessoa-meses** para uma plataforma de escopo limitado. Criar os 68 caminhos restantes sem validação técnica não cumpriria os critérios do próprio roteiro. A lista exata de ausências é emitida pelo auditor para orientar PRs posteriores.

## Critério para mudar um item de estado

Criar código real, teste independente quando houver resultado matemático ou físico, integração com a API pública, documentação de hipóteses, execução CI e revisão do contrato. Evitar contar um arquivo vazio ou um adaptador sem validação como funcionalidade concluída.
