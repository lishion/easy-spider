import unittest
from easy_spider.network.request import Request
from easy_spider.core.env import async_env
from easy_spider.core.spider import AsyncSpider
from test import mock_env


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.num_threads = 4

    def handle(self, response):
        print(response.bs.title)
        yield from super().handle(response)


class TestCore(unittest.TestCase):

    def setUp(self) -> None:
        self.my_spider = MySpider()
        self.my_spider.start_requests = [Request("http://localhost:5000/test_extract")]

    def test_set_default_method(self):
        r = Request("test")
        self.my_spider.method = 'POST'
        self.my_spider.set_default_request_param(r)
        self.assertEqual(r.method, 'POST')

    def test_core(self):
        self.my_spider.method = 'GET'
        async_env.run(self.my_spider)


if __name__ == '__main__':
    unittest.main()
