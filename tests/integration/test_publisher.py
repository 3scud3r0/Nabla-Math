import tempfile
import unittest
from pathlib import Path

from services.publisher.huggingface import publish
from services.publisher.manifest import prepare


class FakeHub:
    def upload_file(self, **kwargs):
        return {"path": kwargs["path_in_repo"], "repo_id": kwargs["repo_id"]}


class PublisherTests(unittest.TestCase):
    def test_receipt_is_idempotent_data(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.jsonl"
            source.write_text('{"x":1}\n', encoding="utf-8")
            manifest = prepare(source, "org/data", "v1", 1)
            receipt = publish(manifest, client=FakeHub(), repo_id="org/data")
            self.assertEqual(receipt["status"], "submitted")
            self.assertEqual(receipt["manifest"]["content_sha256"], manifest.content_sha256)


if __name__ == "__main__":
    unittest.main()
