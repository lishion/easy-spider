from spider.spider import Spider
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
from multiprocessing import Value
from time import sleep
from .log import logger
from .resource import Resource


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
            self._task_queue.push(Resource(url, url, tag="any"))

    def start(self):
        fs = [self._thread_pool.submit(self._run) for _ in range(self._num_threads)]
        wait(fs)

    def _run(self):
        while True:
            with self._lock:
                task = self._task_queue.pop()
                if not task:
                    if self._num_running_task.value == 0:  # 如果 task_queue 为空, 且同时正在进行的任务为0则退出
                        break
                    else:
                        sleep(0)  # 否则 sleep 等待任务
                        continue
            try:
                self._num_running_task.value += 1
                for task in self._spider.crawl(task):
                    self._task_queue.push(task)
            except Exception as e:
                logger.warning(f"{task}处理失败: {e}", exc_info=True)
            finally:
                self._num_running_task.value -= 1
