# NablaMath alpha: primeiro fluxo executável

Esta prévia é **um núcleo pequeno de aritmética racional exata**, desenvolvido depois do acervo histórico. Não implementa Lean, órbitas, fluidos, IA, GPU, compartilhamento de rede ou publicação no Hugging Face. A API pública é experimental.

## Instalar

Requer Python 3.10+. Depois de copiar o repositório, no Windows execute `setup.cmd` no CMD ou `./setup.ps1` no PowerShell; em Linux/macOS execute `sh setup.sh`. O script cria `.venv`, instala o projeto em modo editável e executa `nabla doctor`. Ele não instala Lean nem uma distribuição TeX: são opcionais e devem ser configurados separadamente. Alternativamente: `python -m pip install -e .` no seu ambiente virtual. Não publique um pacote no PyPI apenas por executar este comando.

## Primeiro cálculo

No ambiente instalado:

```text
nabla run "(x+x)/x" --value x=3 --tex report.tex
```

O comando interpreta apenas inteiros, símbolos, as operações `+`, `-`, `*`, `/` e potências inteiras de -32 a 32. `--value x=3` substitui `x` por 3. Frações podem ser dadas como `--value x=3/2`. Decimais e execução de código Python na expressão são rejeitados. O parser limita tamanho e profundidade da expressão, mas ainda não foi auditado como serviço público contra entradas hostis.

O motor armazena a árvore original, aplica `x+x → 2*x` e depois `(2*x)/x → 2`. Ao cancelar, mantém a hipótese `x ≠ 0`; `x=0` gera erro. O resultado é `2` como fração exata. Cada regra é codificada estruturalmente, e o programa confere a igualdade **nessa entrada**. Isso **não** é uma prova formal Lean nem uma verificação universal de toda expressão possível.

O arquivo `.nabla/results.sqlite3` é um banco local SQLite. O identificador é o SHA-256 de entradas, árvore e passos canônicos; copiar o mesmo cálculo não cria outra linha. `nabla show IDENTIFICADOR` lê o registro; `nabla verify IDENTIFICADOR` reexecuta e compara todos os campos. O hash detecta alterações no registro, mas sozinho não autentica o autor nem prova correção matemática.

Para criar o snapshot local:

```text
nabla export snapshot.jsonl
```

Cada linha é um registro reexecutado; o arquivo `snapshot.jsonl.manifest.json` traz contagem e hash do snapshot. Nada é enviado automaticamente à internet. A exportação **não** faz curadoria científica, verificação de licença, divisão de treino/teste ou garantia de qualidade para treinar modelos; essa fase continua no roteiro.

O `.tex` é gerado a partir das transformações registradas. Para tentar compilar PDF acrescente `--pdf` e tenha `pdflatex` funcional. Se a compilação falhar, o `.tex` permanece. O relatório declara a ausência de prova Lean e de validação empírica; não aumenta artificialmente o número de páginas.

## Desenvolver e ampliar

Execute `python -m unittest discover -s tests -v`. Módulos: `expression.py` contém AST/parser/avaliação, `research.py` registra regras e hipóteses, `storage.py` persiste e revalida, `report.py` gera LaTeX, `cli.py` fornece comandos. Uma nova regra deve declarar suas condições, preservar singularidades, ganhar caso positivo/negativo independente e ser registrada na saída. Não inclua solvers, funções transcendentes ou modelos físicos nesta evidência de aritmética racional.

Para alcançar o objetivo maior, siga as fases em [ROADMAP_GLOBAL_RESEARCH.md](ROADMAP_GLOBAL_RESEARCH.md). Em particular, um adaptador Lean terá de conferir a correspondência entre enunciado humano, árvore Python e proposição Lean; só então poderá acrescentar o estado de prova formal a um resultado.
