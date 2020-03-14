from easy_spider.core.spider import AsyncSpider
from easy_spider.log import logger
from easy_spider.network.request import RequestQueue, SimpleRequestQueue
import asyncio
from abc import ABC, abstractmethod


class Task(ABC):

    @abstractmethod
    def run(self): pass


class AbstractTask(Task, ABC):

    def __init__(self, spider, request_queue: RequestQueue):
        self._spider = spider
        self._request_queue = request_queue

    def _init_queue(self):
        if not self._spider.start_requests:
            raise ValueError("初始请求不能为空")
        self._request_queue.put_many(self._spider.start_requests)


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
    def __init__(self, spider: AsyncSpider, request_queue=SimpleRequestQueue()):
        super().__init__(spider, request_queue)
        self._num_running_task = 0
        self._init_queue()

    async def run(self):
        await asyncio.gather(*[self._run() for _ in range(self._spider.num_threads)])

    async def _run(self):
        while True:
            request = self._request_queue.get()
            if request is None:
                if self._num_running_task != 0:
                    await asyncio.sleep(0)
                    continue
                else:  # 如果 task_queue 为空, 且同时正在进行的任务为 0 则退出
                    break
            try:
                self._num_running_task += 1
                new_requests = await self._spider.crawl(request)
                self._request_queue.put_many(new_requests)
                logger.info("成功 {} ".format(request))
            except Exception as e:
                logger.warning("失败 {}  原因 {}".format(request, e))
            finally:
                self._num_running_task -= 1
