import json
import tempfile
import unittest
from pathlib import Path

from nablamath.curation import curate
from nablamath.research import calculate
from nablamath.storage import save_result
from services.publisher.huggingface import publish


class FakeHub:
    def __init__(self):
        self.commits = []

    def create_commit(self, **kwargs):
        self.commits.append(kwargs)
        return "fake-commit"


class PublisherTests(unittest.TestCase):
    def test_validated_snapshot_uploads_data_manifest_card_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            db, snapshot = folder / "store.db", folder / "data.jsonl"
            save_result(db, calculate("x+x", {"x": 2}))
            curated = curate(db, snapshot, license_id="CC0-1.0", provenance="original local computation")
            approval = folder / "approval.json"
            approval.write_text(json.dumps({"approved_for_publication": True,
                "snapshot_sha256": curated["sha256"], "dataset_repo": "org/data",
                "reviewer": "maintainer", "license_id": "CC0-1.0",
                "redistributable": True, "attribution": ""}), encoding="utf-8")
            hub = FakeHub()
            operation = lambda **kwargs: kwargs
            preview = publish(snapshot, approval=approval, repo_id="org/data", client=hub,
                              operation_factory=operation)
            self.assertEqual(preview["status"], "validated")
            self.assertEqual(hub.commits, [])
            submitted = publish(snapshot, approval=approval, repo_id="org/data", client=hub,
                                operation_factory=operation, dry_run=False)
            self.assertEqual(submitted["status"], "submitted")
            self.assertEqual(len(hub.commits), 1)
            ops = hub.commits[0]["operations"]
            self.assertEqual(len(ops), 3)
            self.assertEqual(Path(ops[0]["path_or_fileobj"]).read_bytes(), snapshot.read_bytes())
            self.assertEqual(json.loads(ops[1]["path_or_fileobj"])["content_sha256"], curated["sha256"])
            snapshot.write_text(snapshot.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                publish(snapshot, approval=approval, repo_id="org/data", client=hub,
                        operation_factory=operation, dry_run=False)
            self.assertEqual(len(hub.commits), 1)

    def test_refuses_unapproved_and_cross_split_source(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            db, snapshot = folder / "store.db", folder / "data.jsonl"
            save_result(db, calculate("x+x", {"x": 1}))
            save_result(db, calculate("x+x", {"x": 2}))
            curated = curate(db, snapshot, license_id="CC0-1.0", provenance="local")
            approval = folder / "approval.json"
            decision = {"approved_for_publication": False, "snapshot_sha256": curated["sha256"],
                        "dataset_repo": "org/data", "reviewer": "maintainer", "license_id": "CC0-1.0",
                        "redistributable": True}
            approval.write_text(json.dumps(decision), encoding="utf-8")
            with self.assertRaises(ValueError):
                publish(snapshot, approval=approval, repo_id="org/data", client=None)
            decision["approved_for_publication"] = True
            approval.write_text(json.dumps(decision), encoding="utf-8")
            rows = [json.loads(line) for line in snapshot.read_text(encoding="utf-8").splitlines()]
            rows[1]["split"] = "test" if rows[0]["split"] != "test" else "train"
            raw = "".join(json.dumps(row) + "\n" for row in rows)
            snapshot.write_text(raw, encoding="utf-8")
            import hashlib
            new_hash = hashlib.sha256(raw.encode()).hexdigest()
            manifest_path = snapshot.with_suffix(".jsonl.manifest.json")
            metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
            metadata["sha256"] = new_hash
            metadata["split_counts"] = {s: sum(row["split"] == s for row in rows)
                                        for s in ("train", "validation", "test")}
            manifest_path.write_text(json.dumps(metadata), encoding="utf-8")
            decision["snapshot_sha256"] = new_hash
            approval.write_text(json.dumps(decision), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazamento"):
                publish(snapshot, approval=approval, repo_id="org/data", client=None)
