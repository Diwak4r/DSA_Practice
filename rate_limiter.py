"""Thread-safe rate limiter implementations.

This module provides a base RateLimiter interface and two concrete
implementations: FixedWindowRateLimiter and TokenBucketRateLimiter.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Optional


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def allow_request(self, client_id: str) -> bool:
        """Return True if the request is allowed, False otherwise."""


@dataclass
class _FixedWindowState:
    window_start: float
    count: int
    last_seen: float


class FixedWindowRateLimiter(RateLimiter):
    """Fixed window counter rate limiter.

    Allows up to max_requests within each window of size window_seconds.
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        *,
        time_func: Callable[[], float] = time.monotonic,
        max_idle_seconds: Optional[float] = None,
        cleanup_interval_seconds: float = 300.0,
    ) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if cleanup_interval_seconds <= 0:
            raise ValueError("cleanup_interval_seconds must be positive")

        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._time = time_func
        self._max_idle_seconds = max_idle_seconds
        self._cleanup_interval_seconds = cleanup_interval_seconds

        self._lock = threading.Lock()
        self._clients: Dict[str, _FixedWindowState] = {}
        self._last_cleanup = self._time()

    def allow_request(self, client_id: str) -> bool:
        now = self._time()
        with self._lock:
            self._cleanup_if_needed(now)
            state = self._clients.get(client_id)
            if state is None:
                self._clients[client_id] = _FixedWindowState(
                    window_start=now,
                    count=1,
                    last_seen=now,
                )
                return True

            if now - state.window_start >= self._window_seconds:
                state.window_start = now
                state.count = 0

            state.last_seen = now
            if state.count < self._max_requests:
                state.count += 1
                return True
            return False

    def _cleanup_if_needed(self, now: float) -> None:
        if self._max_idle_seconds is None:
            return
        if now - self._last_cleanup < self._cleanup_interval_seconds:
            return

        cutoff = now - self._max_idle_seconds
        stale_clients = [
            client_id
            for client_id, state in self._clients.items()
            if state.last_seen < cutoff
        ]
        for client_id in stale_clients:
            del self._clients[client_id]
        self._last_cleanup = now


@dataclass
class _TokenBucketState:
    tokens: float
    last_refill: float
    last_seen: float


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter.

    Tokens are refilled at refill_rate tokens per second up to capacity.
    Each request consumes one token.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        time_func: Callable[[], float] = time.monotonic,
        max_idle_seconds: Optional[float] = None,
        cleanup_interval_seconds: float = 300.0,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        if cleanup_interval_seconds <= 0:
            raise ValueError("cleanup_interval_seconds must be positive")

        self._capacity = float(capacity)
        self._refill_rate = float(refill_rate)
        self._time = time_func
        self._max_idle_seconds = max_idle_seconds
        self._cleanup_interval_seconds = cleanup_interval_seconds

        self._lock = threading.Lock()
        self._clients: Dict[str, _TokenBucketState] = {}
        self._last_cleanup = self._time()

    def allow_request(self, client_id: str) -> bool:
        now = self._time()
        with self._lock:
            self._cleanup_if_needed(now)
            state = self._clients.get(client_id)
            if state is None:
                state = _TokenBucketState(
                    tokens=self._capacity - 1.0,
                    last_refill=now,
                    last_seen=now,
                )
                self._clients[client_id] = state
                return True

            state.tokens = self._refill_tokens(state.tokens, state.last_refill, now)
            state.last_refill = now
            state.last_seen = now

            if state.tokens >= 1.0:
                state.tokens -= 1.0
                return True
            return False

    def _refill_tokens(self, tokens: float, last_refill: float, now: float) -> float:
        elapsed = max(0.0, now - last_refill)
        new_tokens = tokens + elapsed * self._refill_rate
        return min(self._capacity, new_tokens)

    def _cleanup_if_needed(self, now: float) -> None:
        if self._max_idle_seconds is None:
            return
        if now - self._last_cleanup < self._cleanup_interval_seconds:
            return

        cutoff = now - self._max_idle_seconds
        stale_clients = [
            client_id
            for client_id, state in self._clients.items()
            if state.last_seen < cutoff
        ]
        for client_id in stale_clients:
            del self._clients[client_id]
        self._last_cleanup = now
