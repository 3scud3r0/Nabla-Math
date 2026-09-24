import unittest

from nablamath.schema.artifact import Artifact
from nablamath.schema.experiment import Experiment
from nablamath.schema.problem import Problem
from nablamath.schema.evidence import Evidence, EvidenceKind
from nablamath.schema.version import require_schema_version


class SchemaTests(unittest.TestCase):
    def test_explicit_version_and_valid_identity(self):
        require_schema_version({"schema_version": 1})
        with self.assertRaises(ValueError):
            require_schema_version({"schema_version": 2})
        self.assertEqual(Problem("first", "Quanto é 1+1?").identifier, "first")
        self.assertEqual(Experiment("exp", "v1", 42, 10).seed, 42)
        self.assertEqual(Evidence(EvidenceKind.COMPUTED, "1+1=2", "a"*64).kind,
                         EvidenceKind.COMPUTED)
        with self.assertRaises(ValueError):
            Artifact("bad", "text/plain", "local", "CC0")
