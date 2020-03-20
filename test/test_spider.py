import unittest
from easy_spider.core.spider import AsyncSpider
from easy_spider.filters.build_in import BloomFilter, all_pass_filter
from easy_spider.network.request import Request
from test.mock_env import run_and_get_result, env


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.start_targets = ["http://localhost:5000/test_extract"]
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
        spider.crawled_filter = BloomFilter(1000, 0.001)
        spider.crawled_filter.pre_filter = all_pass_filter
        start_request = Request.of("http://localhost:5000/test_extract")
        self.assertFalse(spider.crawled_filter.accept(start_request))


if __name__ == '__main__':
    unittest.main()
