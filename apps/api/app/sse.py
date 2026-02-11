import asyncio
from collections import defaultdict
from typing import AsyncGenerator


class LogBroadcaster:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def publish(self, service: str, payload: dict) -> None:
        for queue in list(self._queues[service]):
            await queue.put(payload)

    async def subscribe(self, service: str) -> AsyncGenerator[dict, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._queues[service].append(queue)
        try:
            while True:
                payload = await queue.get()
                yield payload
        finally:
            self._queues[service].remove(queue)
