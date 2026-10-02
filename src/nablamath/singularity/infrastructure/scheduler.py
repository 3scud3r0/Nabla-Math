"""Fair deterministic scheduler for dependency-ready tasks."""

from __future__ import annotations

import heapq

from ..core.planner import Task


class Scheduler:
    def __init__(self) -> None:
        self._queue: list[tuple[int, int, str, Task]] = []
        self._sequence = 0

    def submit(self, task: Task) -> None:
        heapq.heappush(self._queue, (-task.priority, self._sequence, task.identifier, task))
        self._sequence += 1

    def next(self) -> Task | None:
        return heapq.heappop(self._queue)[-1] if self._queue else None

    def __len__(self) -> int:
        return len(self._queue)


__all__ = ["Scheduler"]
