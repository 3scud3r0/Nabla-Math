"""Reproducibility quorum over independent verification receipts.

This is intentionally evidence aggregation, not a truth oracle. Acceptance means
only that the configured independent-verifier policy was satisfied.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .receipts import VerificationReceipt


@dataclass(frozen=True)
class QuorumPolicy:
    min_independent_verifiers: int = 2
    required_methods: frozenset[str] = frozenset()
    reject_on_failed_receipt: bool = True

    def __post_init__(self) -> None:
        if self.min_independent_verifiers < 1:
            raise ValueError("quórum precisa de ao menos um verificador")


@dataclass(frozen=True)
class QuorumDecision:
    status: str
    subject_id: str
    passed_verifiers: tuple[str, ...]
    failed_verifiers: tuple[str, ...]
    methods: tuple[str, ...]
    reason: str

    @property
    def accepted(self) -> bool:
        return self.status == "accepted"


def evaluate_quorum(subject_id: str, receipts: Iterable[VerificationReceipt],
                    policy: QuorumPolicy = QuorumPolicy()) -> QuorumDecision:
    receipts = tuple(receipts)
    relevant = tuple(receipt for receipt in receipts if receipt.subject_id == subject_id)
    passed = {receipt.verifier for receipt in relevant if receipt.outcome == "passed"}
    failed = {receipt.verifier for receipt in relevant if receipt.outcome == "failed"}
    methods = {receipt.method for receipt in relevant if receipt.outcome == "passed"}
    if policy.reject_on_failed_receipt and failed:
        return QuorumDecision("contested", subject_id, tuple(sorted(passed)), tuple(sorted(failed)),
                              tuple(sorted(methods)), "há recibo independente de falha")
    missing_methods = policy.required_methods - methods
    if missing_methods:
        return QuorumDecision("insufficient", subject_id, tuple(sorted(passed)), tuple(sorted(failed)),
                              tuple(sorted(methods)), "faltam métodos: " + ", ".join(sorted(missing_methods)))
    if len(passed) < policy.min_independent_verifiers:
        return QuorumDecision("insufficient", subject_id, tuple(sorted(passed)), tuple(sorted(failed)),
                              tuple(sorted(methods)),
                              f"apenas {len(passed)} verificadores independentes; requer {policy.min_independent_verifiers}")
    return QuorumDecision("accepted", subject_id, tuple(sorted(passed)), tuple(sorted(failed)),
                          tuple(sorted(methods)), "política de reprodutibilidade satisfeita")


__all__ = ["QuorumPolicy", "QuorumDecision", "evaluate_quorum"]