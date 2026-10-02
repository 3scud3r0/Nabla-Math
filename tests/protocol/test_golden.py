import hashlib
import json
from pathlib import Path

from nablamath.network import KnowledgeObject

ROOT = Path(__file__).parents[2]


def test_protocol_schemas_are_json_and_golden_object_matches_digest():
    for path in sorted((ROOT / "protocol/schema").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["$schema"].endswith("2020-12/schema")
        assert data["additionalProperties"] is False
    raw = (ROOT / "protocol/fixtures/golden/problem.json").read_bytes()
    expected = (ROOT / "protocol/fixtures/golden/problem.sha256").read_text().strip()
    assert hashlib.sha256(raw).hexdigest() == expected
    assert KnowledgeObject.from_bytes(raw).to_bytes() == raw
