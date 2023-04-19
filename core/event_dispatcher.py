import asyncio
from typing import Callable, Dict, List, Type


class Event:
    pass

class EventDispatcher:
    __instance = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.event_handlers: Dict[Type[Event], List[Callable]] = {}
            cls.__instance.event_queue = asyncio.Queue()
        return cls.__instance
    
    def register(self, event_class: Type[Event], handler: Callable) -> None:
        if event_class not in self.event_handlers:
            self.event_handlers[event_class] = []
        
        self.event_handlers[event_class].append(handler)

    def unregister(self, event_class: Type[Event], handler: Callable) -> None:
        if event_class in self.event_handlers:
            try:
                self.event_handlers[event_class].remove(handler)
            except ValueError:
                pass

    def dispatch(self, event: Event, *args, **kwargs) -> None:
        asyncio.create_task(self.event_queue.put((event, args, kwargs)))

    async def process_events(self):
        while not self.event_queue.empty():
            event, args, kwargs = await self.event_queue.get()
            event_class = type(event)

            if event_class in self.event_handlers:
                for handler in self.event_handlers[event_class]:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event, *args, **kwargs)
                    else:
                        await asyncio.to_thread(handler, event, *args, **kwargs)

def eda(cls: Type):
    class Wrapped(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.dispatcher = EventDispatcher()
            self.registered_handlers = []

            for _, method in self.__class__.__dict__.items():
                if hasattr(method, "event"):
                    method(instance=self)
                    self.registered_handlers.append((method.event, method))
        
        def __del__(self):
            for event_class, handler in self.registered_handlers:
                self.dispatcher.unregister(event_class, handler)
    
    Wrapped.__name__ = cls.__name__
    Wrapped.__doc__ = cls.__doc__
    return Wrapped

def register_handler(event: Type[Event]):
    def decorator(handler: Callable):
        def wrapper(instance):
            instance.dispatcher.register(event, handler.__get__(instance, instance.__class__))
        wrapper.event = event
        return wrapper
    return decorator