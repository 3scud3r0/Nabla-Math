#ifndef NABLA_FRACTION_H
#define NABLA_FRACTION_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* Sem alocação dinâmica; saída só é modificada em caso de sucesso. */
typedef struct { int64_t numerator; int64_t denominator; } nm_fraction;
/* Retorna 0 em sucesso, -1 em formato/intervalo inválido. */
int nm_parse_fraction(const char *text, nm_fraction *out);
#ifdef __cplusplus
}
#endif
#endif
