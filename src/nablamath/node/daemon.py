"""Servidor HTTP de referência restrito a loopback e iniciado explicitamente."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import re
from threading import Thread

from ..network.store import ContentStore

_OBJECT_PATH = re.compile(r"^/objects/([0-9a-f]{64})$")


class LocalObjectServer:
    def __init__(self, store: ContentStore, token: str, host: str = "127.0.0.1", port: int = 0):
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("servidor de referência só pode escutar em loopback")
        if len(token) < 32:
            raise ValueError("token deve ter ao menos 32 caracteres")
        self.store, self.token = store, token
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/health":
                    return self._send(200, b'{"status":"ok"}', "application/json")
                supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
                if not hmac.compare_digest(supplied, owner.token):
                    return self._send(401, b'{"error":"unauthorized"}', "application/json")
                match = _OBJECT_PATH.fullmatch(self.path)
                if not match:
                    return self._send(404, b'{"error":"not_found"}', "application/json")
                try:
                    raw = owner.store.get(match.group(1)).to_bytes()
                except KeyError:
                    return self._send(404, b'{"error":"not_found"}', "application/json")
                return self._send(200, raw, "application/vnd.nablamath.object+json")

            def _send(self, status: int, body: bytes, content_type: str) -> None:
                self.send_response(status); self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store")
                self.end_headers(); self.wfile.write(body)

            def log_message(self, _format: str, *args: object) -> None:
                return

        self._server = ThreadingHTTPServer((host, port), Handler)
        self._thread: Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        host, port = self._server.server_address[:2]
        return str(host), int(port)

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("servidor já iniciado")
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def close(self) -> None:
        if self._thread is not None:
            self._server.shutdown(); self._thread.join(timeout=5); self._thread = None
        self._server.server_close()


__all__ = ["LocalObjectServer"]
