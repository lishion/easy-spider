from abc import ABC, abstractmethod
from queue import Queue, Empty
from collections import deque


class Request(ABC):
    def __init__(self, url, handler=None, method='GET', priority=0, tag="any",
                 headers=None, cookies=None, timeout=None, params=None, data=None,
                 data_format='form', encoding='utf-8', generation=0):
        self.url: str = url
        self._handler = handler
        self.priority: int = priority
        self.tag = tag
        self.method: str = method
        self.timeout: int = timeout
        self.headers: dict = headers or {}
        self.cookies: dict = cookies or {}
        self.encoding: str = encoding
        self.params: dict = params or {}
        self.data: dict = data
        self.data_format: str = data_format
        self.generation = generation

    @property
    def handler(self):
        return self._handler

    @handler.setter
    def handler(self, callback):
        if not callable(callback):
            raise TypeError("handler must be a callable, but get type: `{}`".format(type(callback).__name__))
        self._handler = callback

    def __repr__(self):
        return "[method={} uri={}]".format(self.method, self.url)

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def of(instance):
        if isinstance(instance, Request):
            return instance
        elif isinstance(instance, str):
            return Request(instance)
        else:
            raise TypeError("can't build request from type `{}`".format(type(instance).__name__))


class RequestQueue(ABC):

    @abstractmethod
    def put(self, request: Request) -> None: pass

    def put_many(self, requests):
        for request in requests:
            self.put(request)

    @abstractmethod
    def get(self) -> Request: pass

    @abstractmethod
    def empty(self) -> bool: pass


class SyncRequestQueue(RequestQueue):

    def __init__(self):
        super().__init__()
        self._queue = Queue()

    def put(self, request: Request) -> None:
        self._queue.put(request)

    def get(self):
        try:
            return self._queue.get_nowait()
        except Empty:
            return None

    def empty(self) -> bool:
        return self._queue.empty()

    def __len__(self):
        return self._queue.qsize()


class SimpleRequestQueue(RequestQueue):

    def __init__(self):
        self._queue = deque()

    def put(self, request: Request) -> None:
        self._queue.append(request)

    def get(self) -> Request:
        try:
            return self._queue.pop()
        except IndexError:
            return None

    def empty(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._queue)