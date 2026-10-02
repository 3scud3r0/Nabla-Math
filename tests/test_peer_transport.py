import tempfile
import unittest
from pathlib import Path

from nablamath.network import (
    ContentStore, KnowledgeObject, PeerServer, QuorumPolicy, VerificationReceipt,
    evaluate_quorum, fetch_object, ping_peer,
)


class PeerTransportTests(unittest.TestCase):
    def _object(self):
        return KnowledgeObject(object_type="experiment", payload={"value": "42", "unit": "1"},
                               license="CC0-1.0", provenance={"tool": "test"})

    def test_tcp_handshake_and_verified_object_transfer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = ContentStore(root / "source")
            destination = ContentStore(root / "destination")
            item = self._object()
            source.put(item)
            with PeerServer(source) as server:
                hello = ping_peer(server.address)
                self.assertEqual(hello["protocol"], "nabla-p2p-v1")
                received = fetch_object(server.address, item.object_id, destination=destination)
            self.assertEqual(received, item)
            self.assertEqual(destination.get(item.object_id), item)

    def test_missing_object_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            with PeerServer(ContentStore(Path(directory) / "store")) as server:
                with self.assertRaises(KeyError):
                    fetch_object(server.address, "0" * 64)


class ReproducibilityQuorumTests(unittest.TestCase):
    def _receipt(self, subject, verifier, outcome="passed", method="exact_reexecution"):
        return VerificationReceipt(subject, verifier, method, outcome, (), "1"*64, "test")

    def test_requires_independent_verifiers_and_surfaces_conflict(self):
        subject = "a" * 64
        policy = QuorumPolicy(2, frozenset({"exact_reexecution"}))
        one = evaluate_quorum(subject, [self._receipt(subject, "lab-a")], policy)
        self.assertEqual(one.status, "insufficient")
        accepted = evaluate_quorum(subject, [self._receipt(subject, "lab-a"), self._receipt(subject, "lab-b")], policy)
        self.assertTrue(accepted.accepted)
        contested = evaluate_quorum(subject, [self._receipt(subject, "lab-a"), self._receipt(subject, "lab-b", "failed")], policy)
        self.assertEqual(contested.status, "contested")


if __name__ == "__main__":
    unittest.main()