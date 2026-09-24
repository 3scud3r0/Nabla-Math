"""Política mínima de elegibilidade; não substitui análise jurídica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LicenseDecision:
    eligible: bool
    license_id: str
    reason: str


def assess(license_id: str, *, redistributable: bool, attribution: str = "") -> LicenseDecision:
    if not license_id.strip():
        return LicenseDecision(False, license_id, "licença ausente")
    if not redistributable:
        return LicenseDecision(False, license_id, "origem não autoriza redistribuição")
    if license_id.upper() in {"NOASSERTION", "UNKNOWN"}:
        return LicenseDecision(False, license_id, "licença não identificada")
    if not attribution.strip() and license_id.upper() not in {"CC0-1.0", "PUBLIC-DOMAIN"}:
        return LicenseDecision(False, license_id, "atribuição necessária")
    return LicenseDecision(True, license_id, "declaração suficiente para o fluxo local")


__all__ = ["LicenseDecision", "assess"]
