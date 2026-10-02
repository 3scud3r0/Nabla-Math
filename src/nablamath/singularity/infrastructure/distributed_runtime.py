"""Authenticated-result contract with a local deterministic reference runtime."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Callable, Mapping

from ..core.planner import Task


@dataclass(frozen=True)
class WorkerResult:
    worker_id: str
    task_id: str
    payload: Mapping[str, object]
    signature: str


def sign_result(worker_id: str, task_id: str, payload: Mapping[str, object], secret: bytes) -> WorkerResult:
    canonical = json.dumps({"worker_id": worker_id, "task_id": task_id, "payload": payload},
                           sort_keys=True, separators=(",", ":")).encode()
    return WorkerResult(worker_id, task_id, payload, hmac.new(secret, canonical, hashlib.sha256).hexdigest())


def verify_result(result: WorkerResult, secret: bytes) -> bool:
    expected = sign_result(result.worker_id, result.task_id, result.payload, secret)
    return hmac.compare_digest(expected.signature, result.signature)


class LocalRuntime:
    def execute(self, task: Task, worker_id: str, secret: bytes,
                handler: Callable[[Task], Mapping[str, object]]) -> WorkerResult:
        return sign_result(worker_id, task.identifier, handler(task), secret)


__all__ = ["LocalRuntime", "WorkerResult", "sign_result", "verify_result"]
