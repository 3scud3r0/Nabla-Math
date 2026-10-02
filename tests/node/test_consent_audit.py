from nablamath.network import KnowledgeObject
from nablamath.node import Consent, ConsentStore, audit_store
from nablamath.network.store import ContentStore


def test_contribution_is_off_by_default_and_consent_roundtrips(tmp_path):
    settings = ConsentStore(tmp_path / "consent.json")
    assert not settings.load().active(100)
    consent = Consent(contribute=True, allow_network=True, expires_unix=200)
    settings.save(consent)
    assert settings.load().active(199)
    assert not settings.load().active(200)


def test_store_audit_reports_missing_references(tmp_path):
    store = ContentStore(tmp_path)
    item = KnowledgeObject("proof", {"value": "x"}, "CC0-1.0", {"kind": "test"}, dependencies=("a" * 64,))
    store.put(item)
    report = audit_store(store)
    assert report.checked == 1
    assert report.missing_dependencies == ("a" * 64,)
    assert not report.ok
