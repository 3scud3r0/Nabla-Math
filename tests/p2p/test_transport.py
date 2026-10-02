import pytest
from nablamath.network import ContentStore, KnowledgeObject
from nablamath.node import LocalObjectServer
from nablamath.p2p import Peer, fetch_object


def test_explicit_loopback_server_requires_token_and_preserves_id(tmp_path):
    store = ContentStore(tmp_path)
    item = KnowledgeObject("problem", {"value": "x"}, "CC0", {"source_id": "test"})
    store.put(item)
    token = "secret-token-that-is-at-least-32-bytes"
    server = LocalObjectServer(store, token); server.start()
    try:
        host, port = server.address
        peer = Peer("a" * 64, f"http://{host}:{port}", frozenset({"objects"}))
        assert fetch_object(peer, item.object_id, token) == item
        with pytest.raises(ConnectionError, match="401"):
            fetch_object(peer, item.object_id, "wrong")
    finally:
        server.close()


def test_server_refuses_non_loopback(tmp_path):
    with pytest.raises(ValueError, match="loopback"):
        LocalObjectServer(ContentStore(tmp_path), "x" * 32, host="0.0.0.0")
