"""Log append-only encadeado por hash; não é uma blockchain nem consenso distribuído."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json


@dataclass(frozen=True)
class Event:
    kind: str
    payload: dict
    previous_hash: str = ""
    created_at: str = ""
    event_hash: str = ""


class EventLog:
    def __init__(self):
        self.events: list[Event] = []

    def append(self, kind: str, payload: dict) -> Event:
        now = datetime.now(timezone.utc).isoformat()
        previous = self.events[-1].event_hash if self.events else "0" * 64
        body = {"kind": kind, "payload": payload, "previous_hash": previous, "created_at": now}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        event = Event(kind, payload, previous, now, digest)
        self.events.append(event)
        return event

    def verify(self) -> bool:
        previous = "0" * 64
        for event in self.events:
            body = {"kind": event.kind, "payload": event.payload,
                    "previous_hash": previous, "created_at": event.created_at}
            expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if expected != event.event_hash:
                return False
            previous = expected
        return True

    def to_data(self) -> list[dict]:
        return [asdict(event) for event in self.events]
