import unittest
from easy_spider.core.spider import AsyncSpider
from easy_spider.network.request import Request
from aiohttp import ClientSession
from asyncio import get_event_loop


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.num_threads = 4

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class TestSpider(unittest.TestCase):

    @staticmethod
    async def async_spider():
        async with ClientSession() as session:
            r = Request("http://localhost:5000/test_extract")
            spider = MySpider()
            spider.set_session(session)
            requests = await spider.crawl(r)
            for request in requests:
                print(request)

    def test_async_spider(self):
        loop = get_event_loop()
        loop.run_until_complete(self.async_spider())


if __name__ == '__main__':
    unittest.main()
