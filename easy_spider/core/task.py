from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.core.recoverable import Recoverable
from easy_spider.log import console_logger, file_logger
from easy_spider.network.request import RequestQueue
from easy_spider.core.queue import get_queue_for_spider
from easy_spider.error.known_error import ClientError
from easy_spider.error.error_formatter import ErrorFormatter, DefaultErrorFormatter, ClientErrorFormatter
import asyncio
from abc import ABC, abstractmethod
from easy_spider.tool import EXE_PATH
from os.path import join, exists


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

    async def wait_request(self):
        request = self._request_queue.get()
        if request is None:
            if self._progress_requests:  # 队列中没有 request, 如果有正在处理中的 request 则等待
                await asyncio.sleep(0.1)
            else:
                return None
        return request

    async def _run(self):
        while True:
            request = await self.wait_request()
            if request is None:  # 如果不存在任何 request 则退出
                break
            else:
                self._progress_requests.append(request)  # 暂存正在处理的 request
            try:
                new_requests = await self._spider.crawl(request)
                self._request_queue.put_many(new_requests)
                console_logger.info("成功 {} ".format(request))
            except Exception as e:
                console_logger.warning("失败 %s %s", request, self._error_formatter.format(e))
                file_logger.warning("失败 %s", request, exc_info=True)
            finally:
                self._progress_requests.remove(request)


class RecoverableTask(AsyncTask, Recoverable):

    def __init__(self, spider: RecoverableSpider, request_queue=None):
        request_queue = request_queue or get_queue_for_spider(spider)
        super().__init__(spider, request_queue)
        self._recover_items = (spider, request_queue)

    def can_recover(self, resource):
        if not exists(resource):
            return False
        for item in self._recover_items:
            if not item.can_recover(resource):
                raise FileNotFoundError("can't recover {}, the file is missing".format(item.recover_name()))
        return True

    def stash(self, resource):
        self._request_queue.put_many(self._progress_requests)  # 需要将所有未被处理的 request 重新放入队列
        for recover_item in self._recover_items:
            recover_item.stash(resource)

    def recover(self, resource):
        if not self.can_recover(resource):
            raise ValueError("{} not exist".format(join(EXE_PATH, resource)))
        for recover_item in self._recover_items:
            recover_item.recover(resource)
