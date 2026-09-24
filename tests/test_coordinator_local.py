from pathlib import Path
import tempfile
import unittest

from nablamath.coordination import LocalCoordinator
from nablamath.research import calculate


class CoordinatorTests(unittest.TestCase):
    def test_two_distinct_workers_and_local_reexecution(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = LocalCoordinator(Path(tmp)/"tasks.db")
            identifier = queue.add("(x+x)/x", {"x": 3})
            self.assertEqual(identifier, queue.add("(x+x)/x", {"x": "3"}))
            a = queue.lease("worker-a")
            self.assertIsNone(queue.lease("worker-a"))
            b = queue.lease("worker-b")
            self.assertEqual(a["task_id"], b["task_id"])
            self.assertIsNone(queue.lease("worker-c"))
            with self.assertRaises(ValueError):
                queue.submit("worker-a", identifier, "0"*64)
            correct = calculate("(x+x)/x", {"x": 3}).content_id
            self.assertEqual(queue.submit("worker-a", identifier, correct), "awaiting_second_worker")
            self.assertEqual(queue.submit("worker-b", identifier, correct), "verified")
            self.assertEqual(queue.status(identifier), "verified")
