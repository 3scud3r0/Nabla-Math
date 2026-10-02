import unittest

from nablamath import __version__
from nablamath.compatibility import normalize_os, runtime_report, support_contract


class CompatibilityTests(unittest.TestCase):
    def test_packaged_contract_matches_package(self):
        contract = support_contract()
        self.assertEqual(contract["package_version"], __version__)
        self.assertEqual(contract["schema_version"], 1)

    def test_supported_runtime(self):
        report = runtime_report(python_version=(3, 10), operating_system="Linux")
        self.assertTrue(report.compatible)
        self.assertEqual(report.operating_system, "linux")
        self.assertEqual(report.problems, ())

    def test_unsupported_runtime_is_explicit(self):
        report = runtime_report(python_version=(3, 15), operating_system="Plan9")
        self.assertFalse(report.compatible)
        self.assertFalse(report.python_supported)
        self.assertFalse(report.operating_system_supported)
        self.assertEqual(len(report.problems), 2)

    def test_os_names_are_normalized(self):
        self.assertEqual(normalize_os("Windows"), "windows")
        self.assertEqual(normalize_os("Darwin"), "macos")


if __name__ == "__main__":
    unittest.main()
