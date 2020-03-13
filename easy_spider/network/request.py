from abc import ABC, abstractmethod
from queue import Queue, Empty
from collections import deque
from typing import List


class Request(ABC):
    def __init__(self, uri, handler=None, method='GET', priority=0, tag="any",
                 headers=None, cookies=None, timeout=None, params=None, data=None,
                 data_format='form', encoding='utf-8'):
        self.uri: str = uri
        self.handler = handler
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

    def __repr__(self):
        return "[method={} uri={}]".format(self.method, self.uri)

    def __str__(self):
        return self.__repr__()


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