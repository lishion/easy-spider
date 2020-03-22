import unittest
from easy_spider.network.request import Request
from easy_spider.core.env import async_env
from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.filters.build_in import GenerationFilter, URLRegFilter
# from test import mock_env


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.num_threads = 4
        self.start_targets = ["http://localhost:5000/test_extract"]

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class MyRecoverableSpider(RecoverableSpider):
    def __init__(self):
        super().__init__()
        self.num_threads = 1
        self.start_targets = ["https://github.blog/"]
        self.filter = URLRegFilter(r"^https://github\.blog/page/\d+/$")
        self.num_threads = 1

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class TestCore(unittest.TestCase):

    def setUp(self) -> None:
        self.my_spider = MySpider()

    # def test_set_default_method(self):
    #     r = Request("test")
    #     self.my_spider.method = 'POST'
    #     self.my_spider._set_default_request_param(r)
    #     self.assertEqual(r.method, 'POST')
    #
    # def test_core(self):
    #     self.my_spider.method = 'GET'
    #     async_env.run(self.my_spider)
    #
    # def test_spider_with_generation_filter(self):
    #     spider = MySpider()
    #     spider.filter = spider.filter + GenerationFilter(max_generation=1)
    #     async_env.run(spider)

    def test_recover(self):
        spider = MyRecoverableSpider()
        with self.assertRaises(ValueError):
            async_env.run(spider)
        spider.name = "test_recover"
        async_env.run(spider)


if __name__ == '__main__':
    unittest.main()
