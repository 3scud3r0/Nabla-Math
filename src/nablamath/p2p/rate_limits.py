"""Janela fixa determinística para limitar abuso por escopo e peer."""

from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if limit < 1 or not 1 <= window_seconds <= 86_400:
            raise ValueError("rate limit inválido")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[int]] = defaultdict(deque)

    def allow(self, key: str, now_unix: int) -> bool:
        if not key or now_unix < 0:
            raise ValueError("chave ou instante inválido")
        events = self._events[key]
        boundary = now_unix - self.window_seconds
        while events and events[0] <= boundary:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now_unix)
        return True


__all__ = ["RateLimiter"]
