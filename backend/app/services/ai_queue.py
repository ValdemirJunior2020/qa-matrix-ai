from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class QueueStatus:
    active: int
    waiting: int
    max_concurrent: int


class AIQueue:
    def __init__(self, max_concurrent: int = 2):
        self.max_concurrent = max_concurrent

        self._semaphore = asyncio.Semaphore(
            max_concurrent
        )

        self._lock = asyncio.Lock()

        self._active = 0
        self._waiting = 0

    async def acquire(self):
        async with self._lock:
            self._waiting += 1

        await self._semaphore.acquire()

        async with self._lock:
            self._waiting -= 1
            self._active += 1

    async def release(self):
        async with self._lock:
            if self._active > 0:
                self._active -= 1

        self._semaphore.release()

    async def status(self) -> QueueStatus:
        async with self._lock:
            return QueueStatus(
                active=self._active,
                waiting=self._waiting,
                max_concurrent=self.max_concurrent,
            )


ai_queue = AIQueue(
    max_concurrent=2
)