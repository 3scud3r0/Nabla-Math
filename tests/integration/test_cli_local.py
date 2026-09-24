import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LocalCliTests(unittest.TestCase):
    def test_run_creates_reproducible_record(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "results.sqlite3"
            process = subprocess.run([sys.executable, "-m", "nablamath.cli", "run", "(x+x)/x",
                                      "--value", "x=3", "--db", str(db)],
                                     capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("Resultado exato: 2", process.stdout)


if __name__ == "__main__":
    unittest.main()
