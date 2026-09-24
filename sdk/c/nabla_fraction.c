#include "nabla_fraction.h"
#include <errno.h>
#include <limits.h>
#include <stddef.h>
#include <stdlib.h>

static uint64_t magnitude(int64_t n) {
    return n < 0 ? (uint64_t)(-(n + 1)) + 1u : (uint64_t)n;
}

static uint64_t gcd_u64(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = a % b; a = b; b = t; }
    return a;
}

int nm_parse_fraction(const char *text, nm_fraction *out) {
    if (!text || !out || !*text) return -1;
    const char *p = text;
    if (*p == '-') ++p;
    if (!*p || (*p == '0' && p[1] != '\0') || (*p < '0' || *p > '9')) return -1;
    for (const char *q = p; *q && *q != '/'; ++q)
        if (*q < '0' || *q > '9') return -1;
    errno = 0;
    char *end = NULL;
    long long numerator = strtoll(text, &end, 10);
    if (errno == ERANGE || end == text) return -1;
    nm_fraction value = {(int64_t)numerator, 1};
    if (*end == '/') {
        if (numerator == 0 || !end[1] || end[1] == '0') return -1;
        p = end + 1;
        if (*p < '1' || *p > '9') return -1;
        for (const char *q = p; *q; ++q)
            if (*q < '0' || *q > '9') return -1;
        errno = 0;
        long long denominator = strtoll(p, &end, 10);
        if (errno == ERANGE || *end || denominator < 2 ||
            gcd_u64(magnitude(numerator), (uint64_t)denominator) != 1) return -1;
        value.denominator = (int64_t)denominator;
    } else if (*end != '\0' || (text[0] == '-' && numerator == 0)) return -1;
    *out = value;
    return 0;
}
