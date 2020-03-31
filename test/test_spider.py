import unittest
from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.filters.build_in import BloomFilter, all_pass_filter, CustomFilter, GenerationFilter
from easy_spider.network.request import Request
from test.mock_env import run_and_get_result, env
from easy_spider.tool import EXE_PATH
from os.path import join


class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["http://localhost:5000/test_extract"]
        self.num_threads = 4

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class RecoverMySpider(RecoverableSpider):

    def init(self):
        self.start_targets = ["http://localhost:5000/test_extract"]
        self.num_threads = 4
        self.filter = self.filter + GenerationFilter(max_generation=1)

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
        start_request = Request.of("http://localhost:5000/test_extract")
        self.assertFalse(spider.crawled_filter.accept(start_request))

    def test_recover(self):
        spider = RecoverMySpider()
        spider.filter = spider.filter + CustomFilter(lambda x: True)
        spider.set_session(env.session)
        list(run_and_get_result(spider.crawl(Request.of("http://localhost:5000/test_extract"))))
        spider.stash(EXE_PATH)
        del spider
        recovered_spider = RecoverMySpider()
        recovered_spider.recover(EXE_PATH)
        self.assertTrue(recovered_spider.crawled_filter.contains(Request.of("http://localhost:5000/a.html")))


if __name__ == '__main__':
    unittest.main()
