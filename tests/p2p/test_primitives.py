import pytest
from nablamath.network import KnowledgeObject
from nablamath.node import IngestPolicy, LocalNode
from nablamath.p2p import Announcement, Peer, PeerDirectory, Quarantine, RateLimiter, ingest_batch, missing


def obj(value, deps=()):
    return KnowledgeObject("problem", {"value": value}, "CC0", {"source_id": value}, dependencies=deps)


def test_peer_directory_tls_expiry_and_capability():
    peer = Peer("a" * 64, "https://node.example", frozenset({"objects"}))
    directory = PeerDirectory(); directory.announce(Announcement(peer, 10, 20))
    assert directory.active(19, "objects") == (peer,)
    assert directory.active(20) == ()
    with pytest.raises(ValueError, match="HTTPS"):
        Peer("b" * 64, "http://example.test", frozenset({"objects"}))


def test_rate_limit_and_quarantine(tmp_path):
    limiter = RateLimiter(2, 10)
    assert limiter.allow("peer", 1) and limiter.allow("peer", 2)
    assert not limiter.allow("peer", 3)
    assert limiter.allow("peer", 11)
    quarantine = Quarantine(tmp_path)
    identifier = quarantine.add(b"untrusted", reason="invalid schema", source="peer:a")
    assert quarantine.ids() == (identifier,)
    quarantine.remove(identifier); assert quarantine.ids() == ()


def test_replication_orders_dependencies(tmp_path):
    root = obj("root")
    leaf = obj("leaf", (root.object_id,))
    policy = IngestPolicy(frozenset({"problem"}), frozenset({"CC0"}))
    node = LocalNode(tmp_path, policy)
    accepted = ingest_batch(node, (leaf, root))
    assert accepted == (root.object_id, leaf.object_id)
    assert missing((root.object_id,), (root.object_id, leaf.object_id)) == (leaf.object_id,)
