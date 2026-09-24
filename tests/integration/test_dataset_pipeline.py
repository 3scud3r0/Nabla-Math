import tempfile
import unittest
from pathlib import Path

from nablamath.dataset import DatasetRecord, export_jsonl


class DatasetPipelineTests(unittest.TestCase):
    def test_snapshot_has_manifest_and_split_counts(self):
        records = [DatasetRecord("a", "train", {"value": 1}, "CC0-1.0", "unit-test")]
        with tempfile.TemporaryDirectory() as directory:
            manifest = export_jsonl(records, Path(directory) / "data.jsonl")
            self.assertEqual(manifest["records"], 1)
            self.assertTrue((Path(directory) / "data.jsonl.manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
