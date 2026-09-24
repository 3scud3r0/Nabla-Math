import json
from pathlib import Path
import tempfile
import unittest

from nablamath.curation import curate
from nablamath.research import calculate
from nablamath.storage import save_result


class CurationTests(unittest.TestCase):
    def test_split_groups_identical_sources_and_requires_attribution(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "results.sqlite3"
            for value in (2, 4):
                save_result(db, calculate("x+x", {"x": value}))
            destination = Path(directory) / "dataset.jsonl"
            with self.assertRaises(ValueError):
                curate(db, destination, license_id="", provenance="local")
            manifest = curate(db, destination, license_id="CC0-1.0", provenance="unit test")
            records = [json.loads(line) for line in destination.read_text().splitlines()]
            self.assertEqual(manifest["records"], 2)
            self.assertEqual(records[0]["split"], records[1]["split"])
            self.assertTrue(all(not entry["formal_proof"] for entry in records))
            self.assertEqual(manifest["publication"], "local_only")
