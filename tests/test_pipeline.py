import tempfile
from pathlib import Path
import unittest

from nablamath.pipeline import Pipeline, Task
from nablamath.pipeline.provenance import provenance_id
from nablamath.store import BlobStore


class PipelineTests(unittest.TestCase):
    def test_dag_reproducibility_and_cycle(self):
        p = Pipeline([Task("x", (), lambda _:3),
                      Task("double", ("x",), lambda dep:2*dep["x"])])
        self.assertEqual(p.run("double"), {"x": 3, "double": 6})
        with self.assertRaises(ValueError):
            Pipeline([Task("a", ("b",), lambda _:0),
                      Task("b", ("a",), lambda _:0)]).run("a")
        self.assertEqual(provenance_id("v1", {"x": 2}, ["b", "a"]),
                         provenance_id("v1", {"x": 2}, ["a", "b"]))

    def test_blob_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            store = BlobStore(Path(directory))
            digest = store.put(b"scientific")
            self.assertEqual(store.get(digest), b"scientific")
            self.assertEqual(store.put(b"scientific"), digest)
            (Path(directory) / digest[:2] / digest).write_bytes(b"altered")
            with self.assertRaises(ValueError):
                store.get(digest)
