# Painel pessoal NablaMath

## Iniciar

- Windows: abrir [Windows installer](https://github.com/3scud3r0/Nabla-Math/actions/workflows/windows-installer.yml), escolher uma execução bem-sucedida, baixar o artefato **NablaMath-Setup-Windows**, extrair e executar o instalador. O instalador usa a conta do usuário, sem privilégios de administrador. O artefato é gerado em Windows pela CI; o projeto não declara instalador disponível até essa execução terminar com sucesso.
- Linux/macOS ou desenvolvimento: instalar Python 3.10+; `python -m pip install .` no repositório (`python -m pip install ".[cloud]"` para habilitar o upload); executar `nabla desktop`. Em modo de desenvolvimento: `PYTHONPATH=src python -m nablamath.desktop.app`.

O botão executável abre `http://127.0.0.1:<porta>/`. Só é acessível neste computador. O SQLite e arquivos ficam em `~/NablaMath` (no Windows, a pasta `NablaMath` do usuário). A desinstalação não apaga o banco pessoal.

## Botões e arquivos

- **Calcular** avalia uma instância racional e salva cada etapa e a hipótese de denominador não nulo no banco.
- **Gerar LaTeX** grava `<identificador>.tex` na pasta pessoal. Para PDF, é preciso compilar o `.tex` com LaTeX instalado.
- **Iniciar loop / Parar** produz até 1.000 instâncias por sessão, a intervalos entre 0,1 e 60 segundos. O loop percorre quatro expressões conhecidas com valores racionais; são exemplos de teste, não resultados originais. O mesmo registro não é gravado duas vezes.
- **Órbita / fluxo** mostram, respectivamente, órbita terrestre circular ideal e solução analítica de fluxo laminar. A viscosidade e densidade da demonstração são fixadas em 1 Pa·s e 1000 kg/m³; a interface não resolve CFD geral.
- **Exportar** cria `verified.jsonl` e `verified.jsonl.manifest.json`. **Importar** lê `incoming.jsonl` e `incoming.jsonl.manifest.json` copiados manualmente para a pasta pessoal. A importação reexecuta e preserva duplicatas idênticas.
- **Criar lote curado** produz `curated.jsonl`, manifesto e cartão na pasta pessoal, separados por expressão.
- **Publicar** pede dataset Hugging Face `conta/nome`, token com escrita, licença, origem, responsável e confirmação de direitos. O sistema confere o hash e reexecuta o lote antes de enviar os três arquivos em um commit. O token é usado nesta requisição, sem ser salvo em disco. O envio pode ser repetido; verificar o destino antes de clicar.

Os registros são aritmética exata para entradas específicas: `formal_proof: false`. Provas Lean opcionais usam `nabla formal ID` no terminal com Lake instalado. Consulte [publicação](PUBLISHING.md), [limites técnicos](IMPLEMENTATION_STATUS.md) e [roteiro](ROADMAP_GLOBAL_RESEARCH.md).
