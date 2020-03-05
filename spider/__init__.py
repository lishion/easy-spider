from .spider import Context
from .extractor import SimpleBSExtractor
from .core import Job, AsyncJob
from .spider import Spider, AsyncSpider
from .request import SimpleRequest, AsyncRequest
from .resource import SimpleResourceQueue
from .handler import CustomHandler
from aiohttp import ClientSession
import asyncio

class SpiderTask:
    def __init__(self, start_urls, extractor_filter):
        self._start_urls = start_urls
        self._extractor_filter = extractor_filter
        self._handlers = []

    def handler(self, filter=None, name="default"):
        def wrapper(func):
            self._handlers.append(
                CustomHandler(func, filter, name)
            )
        return wrapper

    def run(self, num_threads=3):
        context = Context(
            self._handlers,
            SimpleBSExtractor(self._extractor_filter),
            SimpleRequest()
        )
        Job(self._start_urls, Spider(context), SimpleResourceQueue(), num_threads).start()


class AsyncSpiderTask(SpiderTask):

    def __init__(self, start_urls, extractor_filter):
        super().__init__(start_urls, extractor_filter)

    async def _async_run(self, num_threads):
        async with ClientSession() as session:
            context = Context(
                self._handlers,
                SimpleBSExtractor(self._extractor_filter),
                AsyncRequest(session)
            )
            await AsyncJob(self._start_urls,
                           AsyncSpider(context),
                           SimpleResourceQueue(),
                           num_threads).start()

    def run(self, num_threads=3):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_run(num_threads))



