from easy_spider.network.request import Request
from easy_spider.core.spider import AsyncSpider, RecoverableSpider, Spider
from easy_spider.core.recoverable import FileBasedRecoverable
from abc import ABC, abstractmethod
from collections import deque
from os.path import join, exists
from os import makedirs
from easy_spider.tool import *
from easy_spider.log import console_logger
from typing import List


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

    def __bool__(self):
        """
        Python 中逻辑值检测遵循以下准则:
        一个对象在默认情况下均被视为真值，除非当该对象被调用时其所属类定义了 __bool__() 方法且返回 False 或是定义了 __len__() 方法且返回零
        RequestQueue 所有子类均实现了 __len__ 方法。
        但是当:
            def a(request=None):
                request_b = request or SimpleRequestQueue()
            request_a = SimpleRequestQueue()
            a(request_a)
        时，request_a.__len__() 返回 0，导致 request_a or Request() 逻辑检测中 request_a 为假值，此时会生成新的对象。
        而非理想中的 request_b is request_a。
        """
        return len(self) == 0


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
        self._spill_dir_name = 'spill-{}-{}'.format(formatted_datetime('%Y-%m-%d-%H-%M-%S-%f'), uuid())
        self._spill_path = work_path_join(self._spill_dir_name)
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
            pickle_dump(self._wait_spill, self._join(spill_filename))  # spill 到文件
            self._spilled_files.append(spill_filename)  # 记录已经 spill 到磁盘的文件
            self._wait_spill.clear()

    def _may_load(self):
        """
        代理队列为空，则从磁盘加载 requests。优先从已经 spill 到磁盘的文件中加载，如果已经步不存在 spill 到磁盘的文件
        则从 self._wait_spill 中加载
        """
        if self._queue.empty():
            if self._spilled_files:
                spill_file_uri = self._join(self._spilled_files.pop(0))
                try:
                    self.put_many(pickle_load(spill_file_uri))
                except IOError:
                    console_logger.warning(
                        "can't load requests from file `%s`, that's mean you may lost some requests unhandled" % spill_file_uri)
                delete_file(spill_file_uri)  # 加载完成后删除磁盘上的文件
            elif self._wait_spill:
                self.put_many(self._wait_spill)
                self._wait_spill.clear()

    def __len__(self):
        return len(self._queue) + len(self._wait_spill) + len(self._spilled_files) * self._num_of_spill

    def get(self) -> Request:
        self._may_load()
        return self._queue.get()

    def put(self, request: Request) -> None:
        if len(self._queue) >= self._num_of_spill:  # 当代理 queue 中 request 的数量 = self._num_of_spill 时
            self._wait_spill.append(request)  # 新的 request 放入 self._wait_spill 中
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


def get_queue_for_spider(spider):
    if not isinstance(spider, Spider):
        raise TypeError("unknown spider type `{}`".format(spider.__class__.__name__))
    num_of_spill = spider.num_of_spill
    if isinstance(spider, RecoverableSpider):
        queue = RecoverableRequestQueue()
        if num_of_spill:
            return RecoverableSpillRequestQueueProxy(queue, num_of_spill=num_of_spill)
        else:
            return queue
    if isinstance(spider, AsyncSpider):
        queue = SimpleRequestQueue()
        if num_of_spill:
            return SpillRequestQueueProxy(queue, num_of_spill=num_of_spill)
        else:
            return queue
