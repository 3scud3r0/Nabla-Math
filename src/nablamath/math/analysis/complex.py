"""Operações elementares em números complexos com validação numérica."""
import cmath, math


def polar(value: complex) -> tuple[float,float]:
    if not all(math.isfinite(part) for part in (value.real,value.imag)): raise ValueError("complexo não finito")
    return abs(value), cmath.phase(value)


def from_polar(radius: float, angle: float) -> complex:
    if radius<0 or not math.isfinite(radius) or not math.isfinite(angle): raise ValueError("coordenadas polares inválidas")
    return cmath.rect(radius,angle)


def nth_roots(value: complex, degree: int) -> tuple[complex,...]:
    if not 1<=degree<=1_000_000: raise ValueError("grau inválido")
    radius,angle=polar(value); root_radius=radius**(1/degree)
    return tuple(cmath.rect(root_radius,(angle+2*math.pi*k)/degree) for k in range(degree))


def mobius(value: complex, coefficients: tuple[complex,complex,complex,complex]) -> complex:
    a,b,c,d=coefficients; denominator=c*value+d
    if denominator==0: raise ZeroDivisionError("polo da transformação de Möbius")
    if a*d-b*c==0: raise ValueError("transformação de Möbius degenerada")
    return (a*value+b)/denominator

__all__=["from_polar","mobius","nth_roots","polar"]
