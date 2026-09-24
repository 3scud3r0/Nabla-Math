import json
from pathlib import Path
import tempfile
import unittest

from nablamath.research import calculate
from nablamath.storage import export_verified, import_snapshot, load_result, save_result


class ExchangeTests(unittest.TestCase):
    def test_two_local_databases_exchange_verified_work(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = (Path(directory) / n for n in ("a.sqlite3", "b.sqlite3"))
            result = calculate("z+z", {"z": "7/2"})
            save_result(a, result)
            snapshot = Path(directory) / "shared.jsonl"
            export_verified(a, snapshot)
            self.assertEqual(import_snapshot(b, snapshot), (1, 0))
            self.assertEqual(import_snapshot(b, snapshot), (0, 1))
            self.assertEqual(load_result(b, result.content_id)["value"], "7")
            manifest_path = snapshot.with_suffix(".jsonl.manifest.json")
            manifest = json.loads(manifest_path.read_text())
            manifest["sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                import_snapshot(b, snapshot)
