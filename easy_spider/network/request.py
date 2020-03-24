from abc import ABC, abstractmethod
from collections import deque
from easy_spider.core.recoverable import FileBasedRecoverable
from easy_spider.tool import EXE_PATH, uuid, pickle_load, pickle_dump, formatted_datetime, delete_file
from os.path import join, exists
from os import makedirs
from easy_spider.log import console_logger
from typing import List


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

    @abstractmethod
    def __len__(self): pass


# class SyncRequestQueue(RequestQueue):
#
#     def __init__(self):
#         super().__init__()
#         self._queue = Queue()
#
#     def put(self, request: Request) -> None:
#         self._queue.put(request)
#
#     def get(self):
#         try:
#             return self._queue.get_nowait()
#         except Empty:
#             return None
#
#     def empty(self) -> bool:
#         return self._queue.empty()
#
#     def __len__(self):
#         return self._queue.qsize()


class SimpleRequestQueue(RequestQueue):

    def __init__(self):
        self._queue = deque()

    def put(self, request: Request) -> None:
        self._queue.append(request)

    def get(self) -> Request:
        try:
            return self._queue.popleft()
        except IndexError:
            return None

    def clear(self):
        self._queue.clear()

    def empty(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._queue)


class RecoverableRequestQueue(SimpleRequestQueue, FileBasedRecoverable, ABC):

    def __init__(self):
        SimpleRequestQueue.__init__(self)
        FileBasedRecoverable.__init__(self)

    def stash_attr_names(self):
        return ["_queue"]


class SpillRequestQueueProxy(RequestQueue):
    """
        代理类，对 RequestQueue 进行代理，增加在一定条件下将内存中的 request 写入磁盘以节约内存
        当 RequestQueue 为空时，从磁盘加载 requests。
        queue: 需要代理的 RequestQueue
        num_of_spill: 缓存数量
        写入策略: 当 RequestQueue 中 requests 数量 >= num_of_spill 时，将 requests 放入 self._wait_spill 中
        若 len(self._wait_spill) == num_of_spill，则将 self._spilled_files 写入磁盘文件。并将文件名放入 self._spilled_files
        加载策略: 当 RequestQueue 为空时，优先从 self._spilled_files 选取第一个文件加载到 RequestQueue
        否则从 self._wait_spill 中加载。
    """

    def __init__(self, queue: RequestQueue, num_of_spill=10000):
        self._queue = queue
        self._num_of_spill = num_of_spill
        self._spill_dir_name = '.spill-{}-{}'.format(formatted_datetime('%Y-%m-%d-%H-%M-%S-%f'), uuid())
        self._spill_path = join(EXE_PATH, self._spill_dir_name)
        self._wait_spill = []
        self._spilled_files = []

    def empty(self) -> bool:
        return len(self) == 0

    def _join(self, file_name):
        return join(self._spill_path, file_name)

    def _may_spill(self):
        """
        满足条件时，将 requests 写入磁盘
        """
        if len(self._wait_spill) == self._num_of_spill:
            spill_filename = uuid()
            exists(self._spill_path) or makedirs(self._spill_path)
            pickle_dump(self._wait_spill, self._join(spill_filename))
            self._spilled_files.append(spill_filename)
            self._wait_spill.clear()

    def _may_load(self):
        """
        代理队列为空，则从磁盘加载 requests
        """
        if self._queue.empty():
            if self._spilled_files:
                spill_file_uri = self._join(self._spilled_files.pop(0))
                try:
                    self.put_many(pickle_load(spill_file_uri))
                except IOError:
                    console_logger.warning(
                        "can't load requests from file `%s`, that's mean you may lost some requests unhandled" % spill_file_uri)
                delete_file(spill_file_uri)
            elif self._wait_spill:
                self.put_many(self._wait_spill)
                self._wait_spill.clear()

    def __len__(self):
        return len(self._queue) + len(self._wait_spill) + len(self._spilled_files) * self._num_of_spill

    def get(self) -> Request:
        self._may_load()
        return self._queue.get()

    def put(self, request: Request) -> None:
        if len(self._queue) >= self._num_of_spill:
            self._wait_spill.append(request)
            self._may_spill()
        else:
            self._queue.put(request)

    def put_many(self, requests):
        for request in requests:
            self.put(request)


class RecoverableSpillRequestQueueProxy(SpillRequestQueueProxy, FileBasedRecoverable):

    def __init__(self, queue: RecoverableRequestQueue, num_of_spill=10000):
        SpillRequestQueueProxy.__init__(self, queue, num_of_spill)
        FileBasedRecoverable.__init__(self)

    def stash_attr_names(self) -> List[str]:
        return ["_spill_dir_name", "_spill_path", "_spilled_files", "_wait_spill"]

    def stash(self, resource):
        self._queue.stash(resource)
        super().stash(resource)

    def recover(self, resource):
        self._queue.recover(resource)
        if len(self._queue) > self._num_of_spill:  # 为了兼容已经存在的 RecoverableRequestQueue，可以在一段时间后删除
            requests = deque()
            while not self._queue.empty():
                requests.append(self._queue.get())
            while requests:
                self.put(requests.pop())
        try:
            super().recover(resource)
        except:
            pass

    def can_recover(self, resource):
        return self._queue.can_recover(resource)
