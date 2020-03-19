import unittest
from easy_spider.core.spider import AsyncSpider
from easy_spider.network.request import Request
from test.mock_env import run_and_get_result, env


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.num_threads = 4

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class TestSpider(unittest.TestCase):

    async def async_spider(self):
        r = Request("http://localhost:5000/test_extract")
        spider = MySpider()
        spider.set_session(env.session)
        requests = await spider.crawl(r)
        for request in requests:
            print(request)

    def test_async_spider(self):
        run_and_get_result(self.async_spider())

    def test_crawled_spider(self):
        spider = MySpider()
        with self.assertRaises(TypeError):
            spider.crawled_filter = spider.filter


if __name__ == '__main__':
    unittest.main()
