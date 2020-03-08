from abc import ABC, abstractmethod
from queue import Queue, Empty
from collections import deque
from typing import List


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

    @staticmethod
    def get_from(*resource_args):
        num_of_args = len(resource_args)
        if num_of_args == 1:
            url = resource_args[0]
            return Resource(url, url)
        elif 1 < num_of_args <= 4:
            return Resource(*resource_args)
        else:
            raise ValueError("迭代器长度错误，应当[1, 4]，实际为 {}".format(num_of_args))

    @staticmethod
    def of(*resource_args_list) -> List:
        res = []
        for resource_args in resource_args_list:
            if type(resource_args) == str:
                res.append(Resource.get_from(resource_args))
            else:
                res.append(Resource.get_from(*resource_args))
        return res


class ResourceQueue(ABC):

    @abstractmethod
    def put(self, resource: Resource) -> None: pass

    def put_many(self, resources):
        for resource in resources:
            self.put(resource)

    @abstractmethod
    def get(self) -> Resource: pass

    @abstractmethod
    def empty(self) -> bool: pass


class SyncResourceQueue(ResourceQueue):

    def __init__(self):
        super().__init__()
        self._queue = Queue()

    def put(self, resource: Resource) -> None:
        self._queue.put(resource)

    def get(self):
        try:
            return self._queue.get_nowait()
        except Empty:
            return None

    def empty(self) -> bool:
        return self._queue.empty()

    def __len__(self):
        return self._queue.qsize()


class SimpleResourceQueue(ResourceQueue):

    def __init__(self):
        self._queue = deque()

    def put(self, resource: Resource) -> None:
        self._queue.append(resource)

    def get(self) -> Resource:
        try:
            return self._queue.pop()
        except IndexError:
            return None

    def empty(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._queue)