import asyncio
from typing import Any, AsyncIterable, Dict, Tuple

from core.events.base import Event

from .event_handler import EventHandler


class EventWorker:
    def __init__(
        self,
        event_handler: EventHandler,
        cancel_event: asyncio.Event,
        events_in_queue: set,
    ):
        self.event_handler = event_handler
        self.cancel_event = cancel_event
        self.events_in_queue = events_in_queue

        self.queue = asyncio.Queue()
        self.tasks = asyncio.create_task(self._process_events())

    async def _process_events(self):
        async for event, args, kwargs in self._get_event_stream():
            await self.event_handler.handle_event(event, *args, **kwargs)

    async def _get_event_stream(
        self,
    ) -> AsyncIterable[Tuple[Event, Tuple[Any], Dict[str, Any]]]:
        while not self.cancel_event.is_set():
            event, args, kwargs = await self.queue.get()

            yield event, args, kwargs

            self.events_in_queue.remove(event.meta.key)
            self.queue.task_done()

    async def dispatch(self, event: Event, *args, **kwargs) -> None:
        event_key = event.meta.key

        if event_key in self.events_in_queue:
            return

        self.events_in_queue.add(event_key)
        await self.queue.put((event, args, kwargs))

    async def wait(self) -> None:
        await self.queue.join()
