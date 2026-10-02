"""Strict length-prefixed protocol for NablaMath peer transport."""
from __future__ import annotations

import base64
import json
import socket
import struct
from typing import Any, Mapping

PROTOCOL_VERSION = "nabla-p2p-v1"
MAX_FRAME_BYTES = 16 * 1024 * 1024


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"chave duplicada no frame: {key}")
        out[key] = value
    return out


def _validate_message(message: Mapping[str, Any]) -> None:
    kind = message.get("type")
    schemas = {
        "hello": {"type", "protocol", "node_id", "capabilities"},
        "get_object": {"type", "object_id"},
        "object": {"type", "object_id", "payload_b64"},
        "not_found": {"type", "object_id"},
        "ping": {"type", "nonce"},
        "pong": {"type", "nonce"},
    }
    expected = schemas.get(kind)
    if expected is None or set(message) != expected:
        raise ValueError("frame não corresponde ao schema do protocolo")
    if kind == "hello":
        if message["protocol"] != PROTOCOL_VERSION:
            raise ValueError("versão de protocolo incompatível")
        _digest(message["node_id"], "node_id")
        caps = message["capabilities"]
        if not isinstance(caps, list) or any(not isinstance(item, str) or not item for item in caps):
            raise ValueError("capabilities inválidas")
    if kind in {"get_object", "object", "not_found"}:
        _digest(message["object_id"], "object_id")
    if kind == "object":
        if not isinstance(message["payload_b64"], str):
            raise ValueError("payload_b64 inválido")
    if kind in {"ping", "pong"}:
        if not isinstance(message["nonce"], str) or len(message["nonce"]) > 128:
            raise ValueError("nonce inválido")


def _digest(value: Any, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{label} deve ser SHA-256 hexadecimal")


def encode_message(message: Mapping[str, Any]) -> bytes:
    _validate_message(message)
    raw = json.dumps(dict(message), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    if len(raw) > MAX_FRAME_BYTES:
        raise ValueError("frame excede limite do protocolo")
    return struct.pack(">I", len(raw)) + raw


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        part = sock.recv(size - len(chunks))
        if not part:
            raise EOFError("conexão encerrada durante frame")
        chunks.extend(part)
    return bytes(chunks)


def recv_message(sock: socket.socket) -> dict[str, Any]:
    length = struct.unpack(">I", _recv_exact(sock, 4))[0]
    if length < 2 or length > MAX_FRAME_BYTES:
        raise ValueError("comprimento de frame inválido")
    raw = _recv_exact(sock, length)
    try:
        message = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("frame não é JSON UTF-8 válido") from exc
    if not isinstance(message, dict):
        raise ValueError("frame deve ser objeto JSON")
    _validate_message(message)
    return message


def send_message(sock: socket.socket, message: Mapping[str, Any]) -> None:
    sock.sendall(encode_message(message))


def encode_object_payload(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def decode_object_payload(value: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except Exception as exc:
        raise ValueError("payload base64 inválido") from exc


__all__ = ["PROTOCOL_VERSION", "MAX_FRAME_BYTES", "encode_message", "recv_message", "send_message",
           "encode_object_payload", "decode_object_payload"]