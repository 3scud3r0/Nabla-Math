# Compatibilidade suportada

A fonte normativa é o arquivo instalado `nablamath/compatibility.json`; `nabla
doctor` compara o ambiente corrente com esse contrato sem acessar a rede. Alterar
a matriz exige alterar o contrato, executar a CI correspondente e seguir
[`RELEASE_POLICY.md`](RELEASE_POLICY.md).

| Componente | Estado |
| --- | --- |
| Python | `>=3.10,<3.15`; CI de núcleo em 3.10, 3.12 e 3.14 |
| Windows/Linux | Suportados; instalação limpa deve passar na matriz de release |
| macOS | Experimental; não faz parte da garantia de release atual |
| Lean/Mathlib | 4.34.0 fixado em `lean/`; CI GitHub Linux compilou biblioteca e duas instâncias |
| LaTeX | `.tex` gerado; PDF depende de distribuição TeX externa e não foi validado em todos os SOs |
| Numérico | Referências locais pequenas em Python; sem backends GPU nem garantia de desempenho/precisão industrial |
| Serviço global | Ausente; coordenador disponível apenas como classe SQLite local |

Na troca de versão major do Lean ou formato de registro, criar revisão e teste explícito antes de misturar datasets.
