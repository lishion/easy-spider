import unittest
from test.net_mock import NetMockTestCase
from easy_spider.core.spider import AsyncSpider
from easy_spider.network.request import Request
from aiohttp import ClientSession
from asyncio import get_event_loop
from test.tools import test_page


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.num_threads = 4

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class TestSpider(NetMockTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.mocked.get('http://localhost:5000/test_extract',
                        content_type="text/html",
                        body=test_page)

    async def async_spider(self):
        self.prepare()
        r = Request("http://localhost:5000/test_extract")
        spider = MySpider()
        spider.set_session(TestSpider.session)
        requests = await spider.crawl(r)
        for request in requests:
            print(request)

    def test_async_spider(self):
        self.run_and_get_result(self.async_spider())




if __name__ == '__main__':
    unittest.main()
