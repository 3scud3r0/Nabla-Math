# Compatibilidade observada

| Componente | Estado |
| --- | --- |
| Python | `>=3.10` declarado, testes locais em 3.12 e CI em 3.10/3.12; pacote experimental |
| Windows/Linux | Scripts de instalação presentes; não há matriz de instalação limpa validada para todas as versões |
| Lean/Mathlib | 4.34.0 fixado em `lean/`; CI GitHub Linux compilou biblioteca e duas instâncias |
| LaTeX | `.tex` gerado; PDF depende de distribuição TeX externa e não foi validado em todos os SOs |
| Numérico | Referências locais pequenas em Python; sem backends GPU nem garantia de desempenho/precisão industrial |
| Serviço global | Ausente; coordenador disponível apenas como classe SQLite local |

Na troca de versão major do Lean ou formato de registro, criar revisão e teste explícito antes de misturar datasets.
