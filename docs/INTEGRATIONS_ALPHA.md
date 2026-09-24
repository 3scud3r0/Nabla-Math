# Integrações experimentais: Lean, órbitas e curadoria

## Lean 4 / Mathlib

`lean/lean-toolchain` e `lean/lakefile.toml` fixam Lean/Mathlib v4.34.0. Instale `elan` seguindo a documentação do Lean, entre em `lean/` e execute `lake update`, `lake exe cache get`, `lake build`. A CI `.github/workflows/lean-core.yml` verifica a biblioteca e executa duas instâncias geradas no Lean. Para um registro existente: `nabla formal ID --db .nabla/results.sqlite3 --project lean`. Sem Lake ou se a prova falhar, o comando retorna erro; não grava selo formal no SQLite. O gerador substitui os valores numéricos antes de propor igualdade com `norm_num`. Isso **não prova uma identidade simbólica universal, uma teoria física ou fidelidade da formalização de linguagem natural**. O lema `cancel_nonzero_rational` exige `x ≠ 0`. Não aceite conteúdo de fontes externas como código Lean bruto.

## Órbita de dois corpos

`nabla orbit --altitude-m 400000 --svg orbit.svg` imprime parâmetros de órbita terrestre circular ideal e grava SVG escalado no plano, com corpo central em um foco. API: `Orbit(mu_m3_s2, pericenter_m, apocenter_m).summary()`. Usa metros, segundos e m³/s² em toda a API. Constantes [WGS 84 da NGA](https://earth-info.nga.mil/?action=wgs84&dir=wgs84); resultado a 400 km comparado com [ordem de grandeza de velocidade da ISS indicada pela NASA](https://science.nasa.gov/missions/landsat/flying-high-landsat-8-sees-the-international-space-station/) (~7,7 km/s) e [período aproximado](https://science.nasa.gov/earth/earth-observatory/human-spaceflight-factsheet/) (~90 min). Considera massa central pontual, sem atmosfera, J2, pressão de radiação, propulsão nem efemérides reais. Testes conferem conservação independente de energia e momento angular em peri/apoastro. Não serve para navegação de missão.

## Dataset local

`nabla curate dataset.jsonl --db .nabla/results.sqlite3 --license CC0-1.0 --provenance 'meus exemplos autorais'` cria JSONL e manifesto SHA-256. A procedência e licença são **declarações**; autor precisa verificar titularidade. A divisão agrupa registros pela expressão textual sem espaços para reduzir vazamento entre treino e teste; isto não bloqueia expressões equivalentes escritas de outro jeito nem contaminação de outros datasets. `formal_proof: false` permanece verdadeiro no dataset mesmo que uma instância tenha sido verificada isoladamente no Lean, até existir vínculo persistente auditável. O comando não publica nada, não treina modelos e não mede ganho científico.

## Troca entre instalações

`nabla export lote.jsonl --db a.sqlite3` e `nabla import lote.jsonl --db b.sqlite3` permitem aproveitar registros em outra máquina após verificação de manifesto e reexecução. O formato importável aqui é o snapshot bruto produzido por `export`, não o JSONL enriquecido produzido por `curate`. Um hash detecta alteração acidental, mas não autentica a pessoa que enviou o arquivo. Não há API pública, tolerância a nós maliciosos, consenso distribuído, blockchain ou contagem de participantes.
