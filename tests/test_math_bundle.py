from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_math_bundle import build_bundle, mathematical_sources  # noqa: E402


class MathematicalBundleTests(unittest.TestCase):
    def test_bundle_is_complete_deterministic_and_current(self):
        bundle = (ROOT / "math.txt").read_text(encoding="utf-8")
        self.assertEqual(bundle, build_bundle())
        self.assertGreaterEqual(len(mathematical_sources()), 80)
        self.assertGreater(bundle.count("\n"), 4_000)
        for source in mathematical_sources():
            marker = f"BEGIN FILE: {source.relative_to(ROOT).as_posix()}"
            self.assertEqual(bundle.count(marker), 1)

    def test_check_command_is_read_only_and_succeeds(self):
        process = subprocess.run(
            [sys.executable, "tools/build_math_bundle.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)


if __name__ == "__main__":
    unittest.main()
