import hashlib

import pytest

from nablamath.network import ContentStore, KnowledgeObject, export_bundle, join, read_bundle, split


def object_(value="café"):
    return KnowledgeObject("problem", {"value": value}, "CC0-1.0", {"kind": "test"})


def test_unicode_is_normalized_and_noncanonical_input_rejected():
    composed = object_("café")
    decomposed = object_("cafe\u0301")
    assert composed.object_id == decomposed.object_id
    with pytest.raises(ValueError, match="codificação canônica"):
        KnowledgeObject.from_bytes(b'{ "dependencies": [], "license": "CC0-1.0", "object_type": "problem", "parents": [], "payload": {}, "provenance": {}, "schema_version": "nabla-object-v1" }')
    with pytest.raises(ValueError, match="duplicada"):
        KnowledgeObject.from_bytes(b'{"dependencies":[],"dependencies":[],"license":"x","object_type":"problem","parents":[],"payload":{},"provenance":{},"schema_version":"nabla-object-v1"}')


def test_chunks_detect_order_and_content_tampering():
    raw = b"abcdefghij"
    chunks = split(raw, 3)
    assert join(chunks, hashlib.sha256(raw).hexdigest()) == raw
    with pytest.raises(ValueError):
        join(tuple(reversed(chunks)), hashlib.sha256(raw).hexdigest())


def test_offline_bundle_roundtrip_and_id_validation(tmp_path):
    store = ContentStore(tmp_path / "store")
    items = (object_("a"), object_("b"))
    ids = tuple(sorted(store.put(item) for item in items))
    bundle = export_bundle(store, ids, tmp_path / "share.nabla")
    imported = read_bundle(bundle)
    assert tuple(sorted(item.object_id for item in imported)) == ids


def test_migrations_require_an_unambiguous_versioned_path():
    from nablamath.network import MigrationRegistry

    registry = MigrationRegistry()
    registry.register("v0", "v1", lambda data: {**data, "schema_version": "v1", "added": True})
    assert registry.migrate({"schema_version": "v0"}, "v1")["added"] is True
    with pytest.raises(ValueError, match="duplicada"):
        registry.register("v0", "v1", lambda data: data)
    with pytest.raises(ValueError, match="caminho"):
        registry.migrate({"schema_version": "unknown"}, "v1")
