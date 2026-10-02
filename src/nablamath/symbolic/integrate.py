"""Exact symbolic antiderivatives for the declared rational-polynomial subset."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from ..expression import Expr, to_data
from ..math.algebra.groebner import Polynomial, polynomial_from_expr


@dataclass(frozen=True)
class IntegrationCertificate:
    variable: str
    original: Expr
    antiderivative: Expr
    original_terms: tuple[tuple[int, Fraction], ...]
    antiderivative_terms: tuple[tuple[int, Fraction], ...]

    def verify(self) -> bool:
        differentiated: dict[int, Fraction] = {}
        for exponent, coefficient in self.antiderivative_terms:
            if exponent:
                differentiated[exponent - 1] = differentiated.get(exponent - 1, Fraction(0)) + coefficient * exponent
        expected = {exponent: coefficient for exponent, coefficient in self.original_terms if coefficient}
        return differentiated == expected

    def to_data(self) -> dict[str, object]:
        return {"variable": self.variable, "original": to_data(self.original),
                "antiderivative": to_data(self.antiderivative),
                "verified": self.verify(),
                "rule": "rational_polynomial_power_rule"}


def integrate_polynomial(expr: Expr, variable: str) -> IntegrationCertificate:
    """Integrate an exact univariate polynomial, rejecting non-polynomial input."""
    polynomial = polynomial_from_expr(expr, (variable,))
    integrated_terms = {
        (monomial[0] + 1,): coefficient / (monomial[0] + 1)
        for monomial, coefficient in polynomial.terms
    }
    antiderivative = Polynomial((variable,), integrated_terms)
    certificate = IntegrationCertificate(
        variable,
        expr,
        antiderivative.to_expr(),
        tuple((monomial[0], coefficient) for monomial, coefficient in polynomial.terms),
        tuple((monomial[0], coefficient) for monomial, coefficient in antiderivative.terms),
    )
    if not certificate.verify():
        raise ArithmeticError("Certificado de integração falhou")
    return certificate


__all__ = ["IntegrationCertificate", "integrate_polynomial"]
