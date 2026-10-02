"""Cliente limitado para buscar objetos; redirecionamentos e payloads grandes são recusados."""

from __future__ import annotations

from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from ..network.objects import KnowledgeObject
from .peer import Peer


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_object(peer: Peer, object_id: str, token: str, *, max_bytes: int = 2 * 1024 * 1024,
                 timeout: float = 10.0) -> KnowledgeObject:
    if "objects" not in peer.capabilities:
        raise ValueError("peer não anunciou capability objects")
    if len(object_id) != 64 or any(c not in "0123456789abcdef" for c in object_id):
        raise ValueError("object_id inválido")
    request = Request(peer.endpoint.rstrip("/") + "/objects/" + object_id,
                      headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.nablamath.object+json"})
    try:
        with build_opener(_NoRedirect).open(request, timeout=timeout) as response:
            declared = response.headers.get("Content-Length")
            if declared is not None and int(declared) > max_bytes:
                raise ValueError("objeto remoto excede o limite")
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError("objeto remoto excede o limite")
    except HTTPError as exc:
        raise ConnectionError(f"peer respondeu HTTP {exc.code}") from exc
    item = KnowledgeObject.from_bytes(raw)
    if item.object_id != object_id:
        raise ValueError("peer retornou objeto com ID diferente")
    return item


__all__ = ["fetch_object"]
