from abc import abstractmethod

from core.abstract_event_manager import AbstractEventManager


class AbstractSystem(AbstractEventManager):
    @abstractmethod
    def start(self):
        pass
