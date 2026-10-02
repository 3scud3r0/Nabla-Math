import pytest

from nablamath.network import KnowledgeObject
from nablamath.node import IngestPolicy, LocalNode, ResourceBudget


def object_(kind="problem", license="CC0-1.0", **changes):
    values = {"object_type": kind, "payload": {"statement": "1 + 1 = 2"},
              "license": license, "provenance": {"kind": "test"}}
    values.update(changes)
    return KnowledgeObject(**values)


def policy(**changes):
    values = {"allowed_types": frozenset({"problem", "proof", "dataset_manifest"}),
              "allowed_licenses": frozenset({"CC0-1.0"})}
    values.update(changes)
    return IngestPolicy(**values)


def test_local_policy_is_enforced_and_snapshot_is_reproducible(tmp_path):
    node = LocalNode(tmp_path, policy())
    problem = object_()
    assert node.ingest(problem) == problem.object_id
    node.pin(problem.object_id)
    snapshot = node.snapshot("test", "all pinned", "CC0", license="CC0-1.0", provenance={"kind": "test"})
    assert snapshot.payload["object_ids"] == (problem.object_id,)
    assert snapshot.dependencies == (problem.object_id,)


def test_dependencies_must_arrive_first(tmp_path):
    node = LocalNode(tmp_path, policy())
    proof = object_("proof", dependencies=("a" * 64,))
    with pytest.raises(PermissionError, match="dependências ausentes"):
        node.ingest(proof)


def test_license_and_type_are_local_choices(tmp_path):
    node = LocalNode(tmp_path, policy())
    with pytest.raises(PermissionError, match="licença"):
        node.ingest(object_(license="proprietary"))
    with pytest.raises(PermissionError, match="tipo"):
        node.ingest(object_("experiment"))


def test_remote_budget_cannot_exceed_owner_budget():
    owner = ResourceBudget(cpu_seconds=10, memory_bytes=1000, disk_bytes=100, wall_seconds=20)
    assert owner.permits(ResourceBudget(cpu_seconds=5, memory_bytes=500, disk_bytes=50, wall_seconds=10))
    assert not owner.permits(ResourceBudget(cpu_seconds=11, memory_bytes=500, disk_bytes=50, wall_seconds=10))


def test_bounded_task_requires_local_budget_and_declarative_outputs():
    from nablamath.node import BoundedTask

    request = BoundedTask("verify", ("a" * 64,), ("verification_receipt",),
                          ResourceBudget(cpu_seconds=5, memory_bytes=500, disk_bytes=50, wall_seconds=10))
    assert request.accepted_by(ResourceBudget(cpu_seconds=10, memory_bytes=1000, disk_bytes=100, wall_seconds=20))
    assert not request.accepted_by(ResourceBudget(cpu_seconds=4, memory_bytes=1000, disk_bytes=100, wall_seconds=20))
    assert request.to_data()["task_type"] == "verify"
