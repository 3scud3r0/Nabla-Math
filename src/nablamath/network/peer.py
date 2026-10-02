"""Minimal real TCP peer transport for content-addressed NablaMath objects.

The transport verifies protocol version, frame schemas and the object content ID.
It intentionally does not claim NAT traversal, authenticated identities, discovery
or Byzantine consensus; those remain higher protocol layers.
"""
from __future__ import annotations

import secrets
import socket
import socketserver
import threading
from typing import Iterable

from .objects import KnowledgeObject
from .protocol import (
    PROTOCOL_VERSION, decode_object_payload, encode_object_payload, recv_message, send_message,
)
from .store import ContentStore

DEFAULT_CAPABILITIES = ("objects-v1", "ping-v1")


def _hello(node_id: str, capabilities: Iterable[str]) -> dict[str, object]:
    return {"type": "hello", "protocol": PROTOCOL_VERSION, "node_id": node_id,
            "capabilities": sorted(set(capabilities))}


class _ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def _handler(store: ContentStore, node_id: str, capabilities: tuple[str, ...]):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self) -> None:
            self.request.settimeout(10.0)
            try:
                remote = recv_message(self.request)
                if remote["type"] != "hello":
                    return
                send_message(self.request, _hello(node_id, capabilities))
                while True:
                    try:
                        message = recv_message(self.request)
                    except EOFError:
                        return
                    if message["type"] == "ping":
                        send_message(self.request, {"type": "pong", "nonce": message["nonce"]})
                        continue
                    if message["type"] != "get_object":
                        return
                    object_id = message["object_id"]
                    if not store.contains(object_id):
                        send_message(self.request, {"type": "not_found", "object_id": object_id})
                        continue
                    item = store.get(object_id)
                    send_message(self.request, {
                        "type": "object", "object_id": object_id,
                        "payload_b64": encode_object_payload(item.to_bytes()),
                    })
            except (ValueError, OSError):
                return
    return Handler


class PeerServer:
    def __init__(self, store: ContentStore, host: str = "127.0.0.1", port: int = 0, *,
                 node_id: str | None = None, capabilities: Iterable[str] = DEFAULT_CAPABILITIES) -> None:
        self.store = store
        self.node_id = node_id or secrets.token_hex(32)
        self.capabilities = tuple(sorted(set(capabilities)))
        self._server = _ThreadingServer((host, port), _handler(store, self.node_id, self.capabilities))
        self._thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        host, port = self._server.server_address[:2]
        return str(host), int(port)

    def start(self) -> "PeerServer":
        if self._thread is not None:
            return self
        self._thread = threading.Thread(target=self._server.serve_forever, name="nablamath-peer", daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._thread is None:
            self._server.server_close()
            return
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5.0)
        self._thread = None

    def __enter__(self) -> "PeerServer":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _connect(address: tuple[str, int], node_id: str, timeout_s: float) -> tuple[socket.socket, dict[str, object]]:
    sock = socket.create_connection(address, timeout=timeout_s)
    sock.settimeout(timeout_s)
    try:
        send_message(sock, _hello(node_id, DEFAULT_CAPABILITIES))
        remote = recv_message(sock)
        if remote["type"] != "hello":
            raise ValueError("peer não respondeu ao handshake")
        return sock, remote
    except Exception:
        sock.close()
        raise


def ping_peer(address: tuple[str, int], *, timeout_s: float = 5.0) -> dict[str, object]:
    node_id = secrets.token_hex(32)
    sock, remote = _connect(address, node_id, timeout_s)
    try:
        nonce = secrets.token_hex(16)
        send_message(sock, {"type": "ping", "nonce": nonce})
        response = recv_message(sock)
        if response != {"type": "pong", "nonce": nonce}:
            raise ValueError("resposta de ping inválida")
        return remote
    finally:
        sock.close()


def fetch_object(address: tuple[str, int], object_id: str, *, destination: ContentStore | None = None,
                 timeout_s: float = 10.0) -> KnowledgeObject:
    sock, _ = _connect(address, secrets.token_hex(32), timeout_s)
    try:
        send_message(sock, {"type": "get_object", "object_id": object_id})
        response = recv_message(sock)
        if response["type"] == "not_found":
            raise KeyError(object_id)
        if response["type"] != "object" or response["object_id"] != object_id:
            raise ValueError("peer retornou objeto inesperado")
        item = KnowledgeObject.from_bytes(decode_object_payload(response["payload_b64"]))
        if item.object_id != object_id:
            raise ValueError("objeto recebido não corresponde ao hash solicitado")
        if destination is not None:
            destination.put(item)
        return item
    finally:
        sock.close()


__all__ = ["DEFAULT_CAPABILITIES", "PeerServer", "ping_peer", "fetch_object"]