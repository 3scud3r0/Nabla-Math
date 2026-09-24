# Guia de leitura do incremento científico

Este guia explica as fórmulas implementadas e o que cada arquivo efetivamente testa. Abra os arquivos citados enquanto lê. Eles são módulos pequenos de pesquisa e ensino; não constituem um modelo físico universal nem uma nova arquitetura de IA.

## 1. Quantidades e unidades — `schema/units.py`

`Unit.dimensions` tem três expoentes na ordem **massa, comprimento, tempo**. O metro é `(0,1,0)`, o segundo `(0,0,1)`, e m/s é a subtração `(0,1,-1)`. `scale` é uma fração exata: 1 km = 1000 m e 1 h = 3600 s. `Quantity.to` multiplica o valor pela razão das escalas; exige que as dimensões coincidam. Por exemplo, 36 km/h = `36 × 1000 / 3600 = 10 m/s`. Somar quilograma a metro lança erro. Isto não cobre temperatura, corrente elétrica, quantidade de matéria, luminosidade ou unidades com deslocamento afim, como °C; essas extensões exigem uma decisão de modelagem explícita.

## 2. Álgebra linear — `numeric/linear.py`

`solve_exact(A,b)` resolve `Ax=b` por eliminação de Gauss com frações Python (`Fraction`). Para cada coluna, procura um pivô não nulo, troca linhas, divide a linha pelo pivô e zera a coluna nas outras linhas. Sistema singular gera erro: o código não escolhe uma solução arbitrária. Frações exatas removem erro de arredondamento, mas podem crescer muito e tornar matrizes grandes impraticáveis; um backend numérico com estimativa de condicionamento deve ser projetado separadamente.

## 3. EDO — `numeric/ode.py`

`rk4_scalar(f,y0,t0,t1,steps)` aproxima `dy/dt=f(t,y)` dividindo o intervalo em `steps`. A cada passo de largura `h`, mede quatro inclinações: `k1=f(t,y)`, `k2=f(t+h/2,y+h*k1/2)`, `k3=f(t+h/2,y+h*k2/2)` e `k4=f(t+h,y+h*k3)`. Soma `h(k1+2k2+2k3+k4)/6` ao estado. O teste usa `dy/dt=y`, `y(0)=1`, cuja solução conhecida é `y(1)=e`. `refine_error` compara passos `h` e `h/2`; a diferença **não** é um limite matemático rigoroso do erro nem detecta toda instabilidade.

## 4. Derivada — `autodiff/api.py`

Um `Dual` carrega `(valor, derivada direcional)`. Somar duais soma as duas partes. Multiplicar `(a,a')` por `(b,b')` produz `(ab, a'b+ab')`: é a regra do produto. `jvp` injeta a direção inicial e devolve valor e derivada. Para `f(x)=x³+2x` em `x=3`, o retorno é `(33,29)`, pois `f'(x)=3x²+2`. O teste confere isso também por diferenças finitas. Apenas operações implementadas em `Dual` participam da diferenciação; não há VJP, tensores ou grafo de treinamento.

## 5. Fluido — `physics/fluids/model.py`

Para fluido newtoniano incompressível em tubo circular, em regime estacionário, plenamente desenvolvido, laminar e sem deslizamento na parede, o perfil de Hagen–Poiseuille é `v(r)=ΔP(R²−r²)/(4 μ L)`. Aqui `ΔP` é queda de pressão em pascal, `R` raio e `L` comprimento em metros, `μ` viscosidade dinâmica em Pa·s, `r` distância ao centro. A velocidade média é metade da central; a vazão é `Q=πR² v_média`. O teste integra numericamente `v(r)2πr dr` em anéis para conferir a vazão calculada pela fórmula, além de verificar `v(R)=0`. O número de Reynolds `Re=ρ v_média (2R)/μ` é usado apenas como indicador de compatibilidade; `Re<2300` é uma regra prática, sujeita a condições de entrada e perturbações. Isto **não resolve** o problema matemático geral de existência e suavidade de Navier–Stokes nem substitui CFD.

## 6. Coordenador local — `coordination/local.py`

Uma tarefa racional entra no SQLite depois de passar por `calculate`. `lease(worker)` reserva a tarefa por tempo limitado; a operação SQLite `BEGIN IMMEDIATE` evita que duas chamadas locais simultâneas escolham a mesma vaga. `submit` reexecuta o cálculo em vez de acreditar no texto recebido. Dois nomes de trabalhador distintos com o mesmo resultado permitem marcar `verified`. Nomes são meras strings, não pessoas autenticadas: um único usuário pode inventar dois nomes. Por isso não é consenso resistente a fraude, blockchain ou computação global.

## 7. Dados e prova — `curation.py`, `formal.py`

Cada registro é reexecutado antes de entrar em um JSONL local. Expressões com a mesma árvore sintática recebem a mesma divisão train/validation/test para limitar um tipo de vazamento. A divisão não reconhece automaticamente identidades algébricas equivalentes, como `x+x` e `2*x`. Um card deixa claro que a licença informada é declaração do curador. Em Lean, a ponte substitui símbolos por valores racionais e pede ao kernel uma prova de igualdade **daquela instância**; os dois lemas Lean estáticos cobrem a soma de termos iguais e um cancelamento condicionado a `x≠0`. A física orbital, o fluido e o dataset não ganharam prova formal por essa operação.

## 8. Protocolo C/C++/Rust — `protocol/schema/README.md`

Os adaptadores leem apenas frações canônicas dentro de `int64`. Uma string `2/4` é rejeitada porque a forma canônica é `1/2`; `3/1` é rejeitada porque a forma canônica é `3`. A implementação C não aloca memória: escreve em uma estrutura fornecida pelo chamador e retorna erro se a string não respeita o contrato. C++ encapsula esse retorno em `std::optional`; Rust devolve `Option<Fraction>`. Isso já permite testar um pequeno contrato comum, mas não implementa integração geral dos três idiomas com toda a biblioteca.

## Próximas verificações científicas

Formalizar as transformações simbólicas completas sob hipóteses, comparar fluidos com benchmarks experimentais dentro de regime conhecido, validar instaladores em sistemas limpos e medir ganho real em modelos treinados com e sem dados curados. Um grande número de arquivos ou de exemplos verdadeiros não substitui essas avaliações.
