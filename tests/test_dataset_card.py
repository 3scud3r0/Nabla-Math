import json
from pathlib import Path
import tempfile
import unittest

from nablamath.dataset import normalized_expression, write_dataset_card
from nablamath.dataset.quality import assess_record
from nablamath.research import calculate


class DatasetTests(unittest.TestCase):
    def test_structural_key_and_quality(self):
        self.assertEqual(normalized_expression("(x+x)"), normalized_expression("x + x"))
        good = calculate("x+x", {"x": 1}).to_data()
        self.assertTrue(assess_record(good)["training_eligible"])
        good["value"] = "invalid"
        self.assertFalse(assess_record(good)["training_eligible"])

    def test_card_is_explicit_about_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps({"sha256":"a"*64,"records":2,"split_counts":{"train":2},
                                        "license_declaration":"CC0-1.0","provenance":"test"}))
            card = write_dataset_card(path, Path(directory) / "CARD.md")
            self.assertIn("não", card.read_text(encoding="utf-8").lower())
