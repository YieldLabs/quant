import asyncio
from typing import Any, Callable, Optional, Type

from core.commands.base import Command
from core.events.base import Event, EventEnded
from core.queries.base import Query
from infrastructure.config import Config

from .event_handler import EventHandler
from .worker_pool import WorkerPool


class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class EventDispatcher(metaclass=SingletonMeta):
    def __init__(self, config_service: Config):
        self.event_handler = EventHandler()
        self.cancel_event = asyncio.Event()

        config = config_service.get('bus')
        num_workers = config['num_workers']
        piority_groups = config['piority_groups']

        self.command_worker_pool = WorkerPool(
            num_workers, num_workers * piority_groups, self.event_handler, self.cancel_event
        )
        self.query_worker_pool = WorkerPool(
            num_workers, num_workers * piority_groups, self.event_handler, self.cancel_event
        )
        self.event_worker_pool = WorkerPool(
            num_workers, num_workers * piority_groups, self.event_handler, self.cancel_event
        )

    def register(
        self,
        event_class: Type[Event],
        handler: Callable,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> None:
        self.event_handler.register(event_class, handler, filter_func)

    def unregister(self, event_class: Type[Event], handler: Callable) -> None:
        self.event_handler.unregister(event_class, handler)

    async def execute(self, command: Command, *args, **kwargs) -> None:
        await self._dispatch_to_poll(command, self.command_worker_pool, *args, **kwargs)

        await command.wait_for_execution()

    async def query(self, query: Query, *args, **kwargs) -> Any:
        await self._dispatch_to_poll(query, self.query_worker_pool, *args, **kwargs)

        return await query.wait_for_response()

    async def dispatch(self, event: Event, *args, **kwargs) -> None:
        await self._dispatch_to_poll(event, self.event_worker_pool, *args, **kwargs)

    async def _dispatch_to_poll(
        self, event: Type[Event], worker_pool: WorkerPool, *args, **kwargs
    ) -> None:
        if isinstance(event, EventEnded):
            self.cancel_event.set()
            return

        await worker_pool.dispatch_to_worker(event, *args, **kwargs)

    async def wait(self) -> None:
        await self.event_worker_pool.wait()
        await self.query_worker_pool.wait()
        await self.command_worker_pool.wait()

    async def stop(self) -> None:
        await self._dispatch_to_poll(EventEnded(), self.event_worker_pool)
        await self._dispatch_to_poll(EventEnded(), self.query_worker_pool)
        await self._dispatch_to_poll(EventEnded(), self.command_worker_pool)
