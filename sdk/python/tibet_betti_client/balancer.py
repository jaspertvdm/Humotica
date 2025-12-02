"""
BETTI Client-Side Balancer
===========================

Lightweight workload balancer for client applications.
Uses the same physics laws as the server.

Usage:
    from tibet_betti_client.balancer import ClientBalancer, balanced

    # Configure once
    balancer = ClientBalancer(max_heavy=2)

    # Use decorator
    @balanced(weight="heavy")
    async def process_video():
        ...

    # Or context manager
    async with balancer.heavy_task():
        await expensive_operation()

Author: Jasper van de Meent
License: JOSL
"""

import asyncio
import time
from typing import Optional, Callable, Any
from functools import wraps
from dataclasses import dataclass
from threading import Lock


@dataclass
class ClientConfig:
    """Client balancer configuration"""
    max_parallel_heavy: int = 2        # Fewer on client
    max_parallel_medium: int = 4
    cooldown_heavy: float = 0.05       # Longer cooldown on client
    cooldown_medium: float = 0.01
    skip_yield: float = 0.005


class ClientBalancer:
    """Lightweight client-side balancer"""

    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self._lock = Lock()
        self._heavy_running = 0
        self._medium_running = 0
        self._last_heavy = 0.0
        self._last_medium = 0.0
        self._skips = 0

    def can_run_heavy(self) -> bool:
        """Check if heavy task can run"""
        now = time.time()
        with self._lock:
            busy = self._heavy_running >= self.config.max_parallel_heavy
            soon = (now - self._last_heavy) < self.config.cooldown_heavy
            if busy or soon:
                self._skips += 1
                return False
            return True

    def start_heavy(self):
        """Mark heavy task start"""
        with self._lock:
            self._heavy_running += 1
            self._last_heavy = time.time()

    def end_heavy(self):
        """Mark heavy task end"""
        with self._lock:
            self._heavy_running = max(0, self._heavy_running - 1)

    class _HeavyContext:
        def __init__(self, balancer):
            self.balancer = balancer

        async def __aenter__(self):
            while not self.balancer.can_run_heavy():
                await asyncio.sleep(self.balancer.config.skip_yield)
            self.balancer.start_heavy()

        async def __aexit__(self, *args):
            self.balancer.end_heavy()

    def heavy_task(self):
        """Context manager for heavy tasks"""
        return self._HeavyContext(self)

    def get_stats(self) -> dict:
        """Get balancer statistics"""
        with self._lock:
            return {
                "heavy_running": self._heavy_running,
                "skips": self._skips
            }


# Global instance
_default_balancer = ClientBalancer()


def balanced(weight: str = "heavy"):
    """Decorator for balanced async functions"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if weight == "heavy":
                while not _default_balancer.can_run_heavy():
                    await asyncio.sleep(_default_balancer.config.skip_yield)
                _default_balancer.start_heavy()
                try:
                    return await func(*args, **kwargs)
                finally:
                    _default_balancer.end_heavy()
            else:
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_balancer() -> ClientBalancer:
    """Get the default balancer instance"""
    return _default_balancer


def configure(max_heavy: int = 2, cooldown: float = 0.05):
    """Configure the default balancer"""
    global _default_balancer
    config = ClientConfig(max_parallel_heavy=max_heavy, cooldown_heavy=cooldown)
    _default_balancer = ClientBalancer(config)
    return _default_balancer
