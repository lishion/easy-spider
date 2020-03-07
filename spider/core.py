from spider.spider import Spider
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
from multiprocessing import Value
from time import sleep
from .log import logger
from .resource import Resource
import asyncio


class Job:
    def __init__(self, start_urls, spider: Spider, task_queue, num_threads: int = 3):
        self._start_urls = start_urls
        self._spider: Spider = spider
        self._task_queue = task_queue
        self._num_threads = num_threads
        self._thread_pool = ThreadPoolExecutor(max_workers=num_threads)
        self._num_running_task = Value("i", 0)
        self._lock = Lock()
        self._init_queue(start_urls)

    def _init_queue(self, urls):
        for url in urls:
            self._task_queue.put(Resource(url, url, tag="any"))

    def start(self):
        fs = [self._thread_pool.submit(self._run) for _ in range(self._num_threads)]
        wait(fs)

    def _run(self):
        while True:
            with self._lock:
                resource = self._task_queue.get()
                if resource is None:
                    if self._num_running_task.value == 0:  # 如果 task_queue 为空, 且同时正在进行的任务为0则退出
                        break
                    else:
                        sleep(0)  # 否则 sleep 等待任务
                        continue
                else:
                    self._num_running_task.value += 1
            try:
                for resource in self._spider.crawl(resource):
                    self._task_queue.put(resource)
            except Exception as e:
                logger.warning(f"{resource}处理失败: {e}", exc_info=True)
            finally:
                self._num_running_task.value -= 1


class AsyncJob:
    def __init__(self, start_urls, spider: Spider, task_queue, num_threads: int = 3):
        self._start_urls = start_urls
        self._spider: Spider = spider
        self._task_queue = task_queue
        self._num_threads = num_threads
        self._num_running_task = 0
        self._thread_pool = ThreadPoolExecutor(max_workers=num_threads)
        self._init_queue(start_urls)
        self._loop = asyncio.get_event_loop()

    def _init_queue(self, urls):
        for url in urls:
            self._task_queue.put(Resource(url, url, tag="any"))

    async def start(self):
        await asyncio.gather(*[self._run() for i in range(self._num_threads)])

    async def _run(self):
        while True:
            resource = self._task_queue.get()
            if not resource:
                if self._num_running_task == 0:  # 如果 task_queue 为空, 且同时正在进行的任务为0则退出
                    break
                else:
                    await asyncio.sleep(0)
                    continue
            try:
                self._num_running_task += 1
                tasks = await self._spider.crawl(resource)
                for resource in tasks:
                    self._task_queue.put(resource)
            except Exception as e:
                logger.warning(f"{resource}处理失败: {e}", exc_info=True)
            finally:
                self._num_running_task -= 1
