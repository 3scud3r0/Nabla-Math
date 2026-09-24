import tempfile
import unittest
from pathlib import Path

from services.coordinator.app import CoordinatorService
from services.coordinator.auth import token_for
from services.worker.agent import Worker


class CoordinatorTests(unittest.TestCase):
    def test_two_workers_can_verify_same_exact_task(self):
        with tempfile.TemporaryDirectory() as directory:
            service = CoordinatorService(Path(directory) / "queue.sqlite3", secret="secret")
            token = token_for("secret", "alice")
            task_id = service.create_task("alice", token, "1+1", {})
            first = service.scheduler.lease("worker-a")
            second = service.scheduler.lease("worker-b")
            self.assertIsNotNone(first); self.assertIsNotNone(second)
            result_id = Worker("worker-a").execute(first)
            result_id2 = Worker("worker-b").execute(second)
            self.assertEqual(result_id, result_id2)
            self.assertEqual(service.scheduler.submit("worker-a", task_id, result_id), "awaiting_second_worker")
            self.assertEqual(service.scheduler.submit("worker-b", task_id, result_id), "verified")


if __name__ == "__main__":
    unittest.main()
