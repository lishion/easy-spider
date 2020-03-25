from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.core.recoverable import Recoverable, CountDown, FileBasedRecoverable
from easy_spider.log import console_logger, file_logger
from easy_spider.network.request import RequestQueue
from easy_spider.core.queue import get_queue_for_spider
from easy_spider.error.known_error import ClientError
from easy_spider.error.error_formatter import ErrorFormatter, DefaultErrorFormatter, ClientErrorFormatter
import asyncio
from abc import ABC, abstractmethod
from easy_spider.tool import EXE_PATH
from os.path import join, exists
from typing import List


class Task(ABC):

    @abstractmethod
    def run(self): pass


class AbstractTask(Task, ABC):

    def __init__(self, spider, request_queue: RequestQueue):
        self._spider = spider
        self._request_queue = request_queue

    def _init_queue(self):
        if not self._spider.start_targets:
            raise ValueError("初始请求不能为空")
        self._request_queue.put_many(self._spider.start_targets)

    @property
    def spider(self): return self._spider


# class MultiThreadJob(AbstractTask):
#     def __init__(self, spider: MultiThreadSpider, request_queue):
#         super().__init__(spider, request_queue)
#         self._thread_pool = ThreadPoolExecutor(max_workers=spider.start_requests)
#         self._num_running_task = Value("i", 0)
#         self._lock = Lock()
#
#     def run(self):
#         fs = [self._thread_pool.submit(self._run) for _ in range(self._spider.num_threads)]
#         wait(fs)
#
#     def _run(self):
#         while True:
#             with self._lock:
#                 resource = self._request_queue.get()
#                 if resource is None:
#                     if self._num_running_task.value == 0:  # 如果 task_queue 为空, 且同时正在进行的任务为0则退出
#                         break
#                     else:
#                         sleep(0)  # 否则 sleep 等待任务
#                         continue
#                 else:
#                     self._num_running_task.value += 1
#             try:
#                 new_resources = self._spider.crawl(resource)
#                 self._request_queue.put_many(new_resources)
#             except Exception as e:
#                 logger.warning(f"{resource}处理失败: {e}", exc_info=True)
#             finally:
#                 self._num_running_task.value -= 1


class AsyncTask(AbstractTask):

    def __init__(self, spider: AsyncSpider, request_queue=None):
        request_queue = request_queue or get_queue_for_spider(spider)
        super().__init__(spider, request_queue)
        self._init_queue()
        self._progress_requests = []  # 正在处理中的请求
        self._error_formatter = ErrorFormatter(DefaultErrorFormatter())
        self._error_formatter.register(ClientError, ClientErrorFormatter())

    async def run(self):
        await asyncio.gather(*[self._run() for _ in range(self._spider.num_threads)])

    async def _wait_request(self):
        while True:
            request = self._request_queue.get()
            # 当队列中没有 request 且正在处理的 request 不为空，则有可能会有新的request，因此应该等待
            # 否则直接返回 None 表示不会再有新的 request 产生
            if request is None and self._progress_requests:
                await asyncio.sleep(1)
                continue
            return request

    async def _crawl_request(self, request):
        self._progress_requests.append(request)
        try:
            new_requests = await self._spider.crawl(request)
            self._request_queue.put_many(new_requests)
            console_logger.info("成功 {} ".format(request))
        except Exception as e:
            console_logger.warning("失败 %s %s", request, self._error_formatter.format(e))
            file_logger.warning("失败 %s", request, exc_info=True)
        self._progress_requests.remove(request)

    async def _run(self):
        while True:
            request = await self._wait_request()
            if not request:
                break
            await self._crawl_request(request)
        console_logger.info("协程已退出")


class RecoverableTask(AsyncTask, FileBasedRecoverable):

    def __init__(self, spider: RecoverableSpider, request_queue=None):
        request_queue = request_queue or get_queue_for_spider(spider)
        super().__init__(spider, request_queue)
        self._recover_items = (spider, request_queue)
        FileBasedRecoverable.__init__(self)

    def stash_attr_names(self) -> List[str]:
        return ["_progress_requests"]

    def can_recover(self, resource):
        if not exists(resource):
            return False
        for item in self._recover_items:
            if not item.can_recover(resource):
                raise FileNotFoundError("can't recover {}, the file is missing".format(item.recover_name()))
        return True

    def stash(self, resource):
        for recover_item in self._recover_items:
            recover_item.stash(resource)
        super().stash(resource)

    def recover(self, resource):
        if not self.can_recover(resource):
            raise ValueError("{} not exist".format(join(EXE_PATH, resource)))
        for recover_item in self._recover_items:
            recover_item.recover(resource)
        try:
            super().recover(resource)  # todo: 兼容以前的任务，待删除
        except:
            pass
        self._request_queue.put_many(self._progress_requests)  # 将未处理的 request 重新放入队列
        self._progress_requests.clear()  # 清空未处理队列


class CountDownRecoverableTask(RecoverableTask, CountDown):
    def __init__(self, spider: RecoverableSpider, request_queue=None):
        request_queue = request_queue or get_queue_for_spider(spider)
        RecoverableTask.__init__(self, spider, request_queue)
        CountDown.__init__(self, spider.auto_save_frequency)

    async def _crawl_request(self, request):
        await super()._crawl_request(request)
        self.count()
