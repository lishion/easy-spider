from easy_spider.network.client import AsyncClient
from easy_spider.core.task import AsyncTask, RecoverableTask
from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.log import console_logger
from easy_spider.tool import EXE_PATH
from aiohttp import ClientSession
from asyncio import get_event_loop
from cached_property import cached_property
from os.path import join
from os import makedirs
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
        prompt_content = "[*] You entered Ctrl + C, would you like stop spider (y/n): "
        if input(prompt_content).lower() != "y":
            return
        spider_name = task.spider.name
        stash_path = join(EXE_PATH, "." + spider_name)
        if task.can_recover(stash_path):
            prompt_content = "[*] The stash file of spider `{}` already exist, overwrite it?(y/n): ".format(
                spider_name)
            override = input(prompt_content)
            if override.lower() != "y":
                exit()
        else:
            console_logger.info("[*] Create stash dir `{}`".format(stash_path))
            makedirs(stash_path)
        print("[*] Start stash for spider `{}`".format(task.spider.name))
        task.stash(stash_path)
        print("[*] Stash success, exit")
        exit()

    @staticmethod
    def _recover_or_create(spider):
        if not hasattr(spider, "name") or not spider.name:
            raise ValueError("RecoverSpider must have property `name`")
        task = RecoverableTask(spider)
        # 存储爬虫数据的文件夹为 EXE_PATH/.xxx, xxx=spider.name, EXE_PATH 为运行命令执行的文件夹
        stash_path = join(EXE_PATH, "." + spider.name)
        if task.can_recover(stash_path):  # 如果能从文件中恢复则先进行恢复
            print("[*] recover from exist stash file")
            task.recover(stash_path)
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
        return self._loop or get_event_loop()

    def run(self, spider: AsyncSpider):
        self.loop.run_until_complete(self._run_spider(spider))

    def clear(self):
        self.__del__()

    def __del__(self):
        if not self._loop or self.loop.is_closed():
            return
        self._session and self.loop.run_until_complete(self._session.close())


async_env = AsyncSpiderEvn()
