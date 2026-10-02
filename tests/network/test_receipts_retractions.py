import pytest

from nablamath.knowledge import KnowledgeGraph
from nablamath.network import KnowledgeObject, VerificationReceipt, retract


def item(kind="problem", **changes):
    values = {"object_type": kind, "payload": {"value": "base"}, "license": "CC0-1.0",
              "provenance": {"kind": "test"}}
    values.update(changes)
    return KnowledgeObject(**values)


def test_receipt_preserves_subject_environment_and_evidence():
    subject, environment, evidence = item(), item("experiment"), item("proof")
    receipt = VerificationReceipt(subject.object_id, "worker:test", "exact_reexecution", "passed",
                                  (evidence.object_id,), environment.object_id, "same canonical result")
    wrapped = receipt.as_object(license="CC0-1.0", provenance={"kind": "automated_test"})
    assert wrapped.object_type == "verification_receipt"
    assert wrapped.dependencies == tuple(sorted((subject.object_id, environment.object_id, evidence.object_id)))


def test_retraction_is_an_additive_object_not_deletion():
    target, replacement = item(), item(payload={"value": "corrected"})
    notice = retract(target.object_id, reason="incorrect", explanation="counterexample found",
                     replacements=(replacement.object_id,), license="CC0-1.0", provenance={"kind": "review"})
    graph = KnowledgeGraph((target, replacement, notice))
    assert graph.retractions()[target.object_id] == (notice.object_id,)
    assert target.object_id in graph.objects


def test_receipt_rejects_unknown_claims():
    with pytest.raises(ValueError, match="método"):
        VerificationReceipt("a" * 64, "worker", "trust_me", "passed", (), "b" * 64, "ok")
