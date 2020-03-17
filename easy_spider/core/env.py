from easy_spider.network.client import AsyncClient
from easy_spider.core.task import AsyncTask
from easy_spider.core.spider import AsyncSpider
from aiohttp import ClientSession
from asyncio import get_event_loop
from cached_property import cached_property


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

    async def _run_spider(self, spider):
        self._prepare()
        spider.set_session(self._session)
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
