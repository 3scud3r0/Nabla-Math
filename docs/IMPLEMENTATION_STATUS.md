# Estado de implementação

Revisado em 24/09/2026. Este documento resume protótipos e limites observáveis. O checklist e os arquivos restantes estão em [`ROADMAP_GLOBAL_RESEARCH.md`](ROADMAP_GLOBAL_RESEARCH.md).

## Funciona neste recorte

- Pacote Python experimental, CLI e desktop local em loopback.
- Expressões racionais em subconjunto documentado, etapas com condições, SQLite, importação/exportação JSONL, manifesto/hash e LaTeX fonte.
- Exemplos limitados de Lean 4/Mathlib, órbita ideal de dois corpos, fluxo laminar analítico em tubo, unidades/conversões, RK4 e visualização SVG.
- Curadoria local, exportação e publicador Hugging Face opt-in; worker declarativo local; protótipos de fila e log Merkle.
- Parsers de frações em C/C++/Rust; instalador Windows alpha.
- Site estático publicado: <https://3scud3r0.github.io/Nabla-Math/>.

## Ainda não demonstrado

- O serviço global: `services/coordinator/app.py` só expõe uma rota HTTP `/health`; não há API pública de coordenação multiusuário.
- Participantes ou tarefas reais ao vivo: contadores versionados não representam usuários conectados.
- Dataset NablaMath publicado no Hugging Face ou ganho de modelos treinados com esses dados.
- Provas Lean gerais para as regras simbólicas, validação independente de enunciado formalizado ou autoformalização geral.
- Validação orbital por efemérides externas, CFD geral, simulação física de alta fidelidade ou garantia de aplicação industrial.
- Execução segura de código arbitrário de agente em sandbox de produção; workers atuais executam apenas a tarefa declarativa restrita.
- SDKs completos dos motores científicos em C/C++/Rust: os componentes existentes cobrem parsing de frações.

## Operação externa pendente

Para uma publicação de dataset são necessários um lote autorizado, revisão humana de direitos/privacidade, repositório Hugging Face de destino e segredo `HF_TOKEN`. Para uma rede distribuída são necessários serviço hospedado, operador responsável, autenticação, política de privacidade, monitoramento, backup e testes com máquinas distintas. O site GitHub Pages não fornece backend.

As fases F0–F6 permanecem abertas até os critérios de aceite do roadmap serem satisfeitos com evidência revisável. Uma contagem de arquivos ou testes unitários isolados não fecha uma fase.
