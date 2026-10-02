import json

import pytest

from nablamath.network import ContentStore, DatasetManifest, KnowledgeObject


def problem(**changes):
    values = {
        "object_type": "problem",
        "payload": {"statement": "x + 1 = 2", "domain": "integer"},
        "license": "CC-BY-4.0",
        "provenance": {"kind": "human_original", "source": "test fixture"},
    }
    values.update(changes)
    return KnowledgeObject(**values)


def test_object_id_is_canonical_and_roundtrips():
    first = problem(payload={"statement": "x + 1 = 2", "domain": "integer"})
    second = problem(payload={"domain": "integer", "statement": "x + 1 = 2"})
    assert first.object_id == second.object_id
    assert KnowledgeObject.from_bytes(first.to_bytes()) == first
    assert json.loads(first.to_bytes())["schema_version"] == "nabla-object-v1"


def test_rejects_ambiguous_numbers_and_unsorted_relationships():
    with pytest.raises(ValueError, match="floats não são canônicos"):
        problem(payload={"approximation": 0.1})
    digest_a, digest_b = "a" * 64, "b" * 64
    with pytest.raises(ValueError, match="ordenado"):
        problem(parents=(digest_b, digest_a))


def test_store_detects_tampering(tmp_path):
    store = ContentStore(tmp_path)
    item = problem()
    assert store.put(item) == item.object_id
    assert store.put(item) == item.object_id
    assert store.get(item.object_id) == item
    path = tmp_path / item.object_id[:2] / item.object_id[2:]
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        store.get(item.object_id)


def test_manifest_commits_to_sorted_members():
    one = problem()
    two = problem(payload={"statement": "x + 2 = 4", "domain": "integer"})
    members = tuple(sorted((one.object_id, two.object_id)))
    manifest = DatasetManifest("álgebra básica", members, "reexecução exata", "CC-BY-4.0")
    wrapped = manifest.as_object(provenance={"kind": "test"}, license="CC-BY-4.0")
    assert wrapped.payload["merkle_root"] == manifest.root
    assert wrapped.dependencies == members


def test_payload_is_deeply_immutable_and_id_cannot_go_stale():
    source = {"nested": [{"value": "original"}]}
    item = problem(payload=source)
    source["nested"][0]["value"] = "mutated outside"
    assert item.payload["nested"][0]["value"] == "original"
    with pytest.raises(TypeError):
        item.payload["nested"][0]["value"] = "mutated inside"
    assert KnowledgeObject.from_bytes(item.to_bytes()).object_id == item.object_id
