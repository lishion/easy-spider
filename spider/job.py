from spider.spider import Spider
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
from multiprocessing import Value
from time import sleep
from .log import logger
from .resource import ResourceQueue
import asyncio
from abc import ABC, abstractmethod


class Job(ABC):

    @abstractmethod
    def start(self): pass


class AbstractJob(Job, ABC):

    def __init__(self, start_resources, spider, resource_queue: ResourceQueue, num_threads=3):
        self._start_resources = start_resources
        self._spider = spider
        self._resource_queue = resource_queue
        self._num_threads = num_threads
        self._init_resource_queue()

    def _init_resource_queue(self):
        self._resource_queue.put_many(self._start_resources)


class MultiThreadJob(AbstractJob):
    def __init__(self, start_urls, spider: Spider, resource_queue, num_threads: int = 3):
        super().__init__(start_urls, spider, resource_queue, num_threads)
        self._thread_pool = ThreadPoolExecutor(max_workers=num_threads)
        self._num_running_task = Value("i", 0)
        self._lock = Lock()

    def start(self):
        fs = [self._thread_pool.submit(self._run) for _ in range(self._num_threads)]
        wait(fs)

    def _run(self):
        while True:
            with self._lock:
                resource = self._resource_queue.get()
                if resource is None:
                    if self._num_running_task.value == 0:  # 如果 task_queue 为空, 且同时正在进行的任务为0则退出
                        break
                    else:
                        sleep(0)  # 否则 sleep 等待任务
                        continue
                else:
                    self._num_running_task.value += 1
            try:
                new_resources = self._spider.crawl(resource)
                self._resource_queue.put_many(new_resources)
            except Exception as e:
                logger.warning(f"{resource}处理失败: {e}", exc_info=True)
            finally:
                self._num_running_task.value -= 1


class AsyncJob(AbstractJob):
    def __init__(self, start_resources, spider: Spider, resource_queue, num_threads: int = 3):
        super().__init__(start_resources, spider, resource_queue, num_threads)
        self._num_running_task = 0
        self._loop = asyncio.get_event_loop()

    async def start(self):
        await asyncio.gather(*[self._run() for i in range(self._num_threads)])

    async def _run(self):
        while True:
            resource = self._resource_queue.get()
            if resource is None:
                if self._num_running_task == 0:  # 如果 task_queue 为空, 且同时正在进行的任务为0则退出
                    break
                else:
                    await asyncio.sleep(0)
                    continue
            else:
                self._num_running_task += 1
            try:
                new_resources = await self._spider.crawl(resource)
                self._resource_queue.put_many(new_resources)
            except Exception as e:
                logger.warning(f"{resource}处理失败: {e}", exc_info=True)
            finally:
                self._num_running_task -= 1
