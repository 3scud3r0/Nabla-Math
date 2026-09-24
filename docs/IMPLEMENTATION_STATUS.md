# Cobertura do inventário e limites de entrega

Auditoria automática: `python tools/roadmap_status.py`. Na revisão de 24/09/2026, **122 de 122 caminhos específicos** do inventário existem; esse número conta a presença do arquivo, **não** sua conclusão. Os novos módulos têm contratos executáveis e testes locais, mas várias integrações continuam opt-in e as fases científicas/global ainda não estão concluídas.

## Fluxos já executáveis

1. Aritmética racional exata, etapas condicionais, SQLite, JSONL e LaTeX fonte.
2. Lean/Mathlib fixados e duas instâncias racionais compiladas em CI anterior.
3. Órbita de dois corpos ideal em SI e SVG; fluxo laminar analítico em tubo com conferência por quadratura.
4. Conversões dimensionais exatas, álgebra linear racional, RK4 e JVP escalar por duais.
5. Propostas declarativas de agente com cota, trajetória de falhas e recusa de execução arbitrária.
6. Curadoria local com hash, cartão, divisão estrutural; coordenação SQLite local e raiz Merkle, sem autenticação de usuários.
7. Parser C e wrapper C++ compilados; parser Rust submetido à CI de interoperabilidade.
8. Adaptadores opcionais NumPy/SciPy/SymPy, relatórios/viz, propagação radial reduzida de dois corpos via RK4, seleção de agentes, schema/export de dataset e serviço loopback com token HMAC.
9. Ponte formal reorganizada como pacote `nablamath.formal`, arquivos Lean de referência, publicador opt-in de snapshot curado, com auditoria e commit único e site estático com fonte modular.

## Bloqueios para concluir todas as fases

- O [inventário atualizado](ROADMAP_GLOBAL_RESEARCH.md) inclui ainda CFD validado em referências externas, traduções Lean simbólicas completas, web service autenticado e resistente a fraude, operação efetiva de publicação diária no Hugging Face, avaliação de treinamento e suporte geral Rust/C/C++. Requerem projeto, dados, manutenção e revisão especializada.
- O código novo recebeu MIT em `LICENSE`; dados, arquivos históricos e dependências de terceiros continuam sujeitos às licenças declaradas em seus próprios metadados. A política de contribuição e a operação pública ainda precisam de aprovação do mantenedor.
- O workflow diário exige snapshot e aprovação associados ao hash, além de variáveis do repositório e segredo do Hub; não há credenciais, organização nem lote aprovado no repositório. Site e dataset público não foram ativados. Ver [publicação](PUBLISHING.md).
- O plano original estima **44–115 pessoa-meses** para uma plataforma de escopo limitado. Criar os caminhos restantes reduziu a ausência de arquivos, mas não transforma adaptadores opt-in em produto global nem substitui validação técnica. O auditor confirma presença; os critérios de fase continuam sendo testes, evidência e operação.

## Critério para mudar um item de estado

Criar código real, teste independente quando houver resultado matemático ou físico, integração com a API pública, documentação de hipóteses, execução CI e revisão do contrato. Evitar contar um arquivo vazio ou um adaptador sem validação como funcionalidade concluída.
