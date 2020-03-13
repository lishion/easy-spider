import unittest
from easy_spider.network.request import Request
from easy_spider.core.env import async_env
from test.test_spider import MySpider


class TestCore(unittest.TestCase):

    def setUp(self) -> None:
        self.my_spider = MySpider()
        self.my_spider.start_requests = [Request("http://localhost:5000/test_extract")]

    def test_set_default_method(self):
        r = Request("test")
        self.my_spider.set_default_request_param(r)
        self.assertEqual(r.method, 'GET')

    def test_core(self):
        async_env.run(self.my_spider)


if __name__ == '__main__':
    unittest.main()
