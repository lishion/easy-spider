from easy_spider.network.client import AsyncClient
from easy_spider.core.task import AsyncTask, RecoverableTask, CountDownRecoverableTask
from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.log import console_logger
from easy_spider.tool import EXE_PATH, work_path_join
from aiohttp import ClientSession
from asyncio import get_event_loop
from cached_property import cached_property
from os.path import join
from os import makedirs
from os.path import exists
import signal


class AsyncSpiderEvn:
    def __init__(self, loop=None):
        self._client = None
        self._loop = loop
        self._session = None

    def _prepare(self):
        if self._session is None:
            self._session = ClientSession()
        if self._client is None:
            self._client = AsyncClient()

    @staticmethod
    def _when_interrupt(_, __, task):
        if input("[*] You entered Ctrl + C, would you like stop spider (y/n): ").lower() != "y":
            return
        if input("[*] Would you like stash your spider task (y/n): ").lower() != "y":
            exit()
        spider_name = task.spider.name
        stash_path = work_path_join(spider_name)
        if task.can_recover(stash_path):
            prompt_content = "[*] The stash file of spider `{}` already exist, overwrite it?(y/n): ".format(
                spider_name)
            override = input(prompt_content)
            if override.lower() != "y":
                exit()
        print("[*] Start stash for spider `{}`".format(task.spider.name))
        task.stash(stash_path)
        print("[*] Stash success, exit")
        exit()

    @staticmethod
    def _recover_or_create(spider):
        if not hasattr(spider, "name") or not spider.name:
            raise ValueError("RecoverSpider must have property `name`")
        # 存储爬虫数据的文件夹为 EXE_PATH/.xxx, xxx=spider.name, EXE_PATH 为运行命令执行的文件夹
        stash_path = work_path_join(spider.name)
        if spider.auto_save_frequency != -1:
            task = CountDownRecoverableTask(spider)
            task.add_actions(lambda: task.stash(stash_path))  # 自动保存频率不为 1，则添加自动保存回调函数
        else:
            task = RecoverableTask(spider)
        if task.can_recover(stash_path):  # 如果能从文件中恢复则先进行恢复
            print("[*] recover from exist stash file")
            task.recover(stash_path)
        exists(stash_path) or makedirs(stash_path)
        return task

    async def _run_spider(self, spider):
        self._prepare()
        spider.set_session(self._session)
        if isinstance(spider, RecoverableSpider):
            task = self._recover_or_create(spider)

            def callback_when_interrupt(signum, frame):
                self._when_interrupt(signum, frame, task)

            signal.signal(signal.SIGINT, callback_when_interrupt)
            signal.signal(signal.SIGTERM, callback_when_interrupt)
        else:
            task = AsyncTask(spider)
        await task.run()

    @cached_property
    def loop(self):
        if not self._loop:
            self._loop = get_event_loop()
        return self._loop

    def run(self, spider: AsyncSpider):
        self.loop.run_until_complete(self._run_spider(spider))

    def clear(self):
        self.__del__()

    def __del__(self):
        if not self.loop or self.loop.is_closed():
            return
        self._session and self.loop.run_until_complete(self._session.close())


async_env = AsyncSpiderEvn()
