"""API local opcional, apenas loopback por padrão, usando a biblioteca padrão."""

from __future__ import annotations

from dataclasses import asdict
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from .auth import authenticate
from .events import EventLog
from .scheduler import Scheduler


class CoordinatorService:
    def __init__(self, database: str | Path, *, secret: str):
        self.scheduler = Scheduler(database)
        self.secret = secret
        self.events = EventLog()

    def create_task(self, participant_id: str, token: str, expression: str, values: dict) -> str:
        principal = authenticate(self.secret, participant_id, token, frozenset({"write"}))
        task_id = self.scheduler.add(expression, values)
        self.events.append("task.created", {"task_id": task_id, "participant": principal.participant_id})
        return task_id

    def lease(self, participant_id: str, token: str) -> dict | None:
        authenticate(self.secret, participant_id, token)
        return self.scheduler.lease(participant_id)

    def start_http(self, host: str = "127.0.0.1", port: int = 0):
        service = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                if self.path != "/health":
                    self.send_error(404)
                    return
                body = json.dumps({"ok": True, "events": len(service.events.events)}).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_args):
                return
        server = ThreadingHTTPServer((host, port), Handler)
        Thread(target=server.serve_forever, daemon=True).start()
        return server


__all__ = ["CoordinatorService"]
