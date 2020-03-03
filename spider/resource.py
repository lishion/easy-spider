from abc import ABC, abstractmethod
from queue import Queue, Empty


class Resource(ABC):
    def __init__(self, uri, key, priority=0, tag=None):
        self.uri = uri
        self.key = key
        self.priority = priority
        self.tag = tag or "any"

    def __repr__(self):
        return f"[uri={self.uri}, key={self.key}, tag={self.tag}]"

    def __str__(self):
        return self.__repr__()


class ResourceQueue(ABC):

    @abstractmethod
    def push(self, resource: Resource) -> None: pass

    @abstractmethod
    def pop(self) -> Resource: pass

    @abstractmethod
    def empty(self) -> bool: pass


class SimpleResourceQueue(ResourceQueue):

    def __init__(self):
        super().__init__()
        self._queue = Queue()

    def push(self,  resource: Resource) -> None:
        self._queue.put(resource)

    def pop(self):
        try:
            return self._queue.get_nowait()
        except Empty:
            return None

    def empty(self) -> bool:
        return self._queue.empty()
