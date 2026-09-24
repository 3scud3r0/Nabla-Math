# SDK C experimental

`cc -std=c11 -Wall -Wextra -Werror -c sdk/c/nabla_fraction.c`. `nm_parse_fraction` lê o subconjunto canônico de [`protocol/schema/README.md`](../../protocol/schema/README.md) e escreve dois `int64_t`. Retorno 0 significa sucesso; -1 não modifica a saída. O chamador é dono da memória. Sem promessas de ABI estável; a evolução requer versionamento e teste cruzado.
