import unittest
from easy_spider.error.known_error import *
from asyncio import TimeoutError
from aiohttp.client_exceptions import ClientConnectionError
from easy_spider.error.error_formatter import ClientErrorFormatter, DefaultErrorFormatter, ErrorFormatter
from easy_spider.error.error_handler import handler_error, client_error, forward
from easy_spider.error.known_error import ClientError, ResponseError
from easy_spider.core.spider import AsyncSpider
from easy_spider import Request
from test import mock_env


@forward(to=handler_error)
def handler():
    raise ValueError("输入错误")


@forward(to=client_error)
def do_request():
    raise TimeoutError()


class Spider(AsyncSpider):
    def __init__(self):
        super().__init__()

    def handle(self, response):
        raise ValueError("输入错误")


class TestExceptionFormatter(unittest.TestCase):

    def test_formatter(self):
        formatter = ErrorFormatter(DefaultErrorFormatter())
        formatter.register(ClientError, ClientErrorFormatter())

        try:
            raise ConnectionError() from ClientConnectionError()
        except Exception as e:
            self.assertIn("aiohttp.client_exceptions.ClientConnectionError", ClientErrorFormatter().format(e))

        try:
            raise ConnectionError() from TimeoutError()
        except Exception as e:
            self.assertIn("超时", ClientErrorFormatter().format(e))

        try:
            raise HandlerError() from ValueError("输入错误")
        except Exception as e:
            self.assertIn("输入错误", DefaultErrorFormatter().format(e))

        try:
            raise ValueError("输入错误")
        except Exception as e:
            self.assertIn("输入错误", DefaultErrorFormatter().format(e))

    def test_handler(self):
        with self.assertRaises(HandlerError):
            handler()

        with self.assertRaises(ClientError):
            do_request()

    def test_spider_handler(self):
        spider = Spider()
        spider.set_session(mock_env.env.session)
        formatter = ErrorFormatter(DefaultErrorFormatter())
        formatter.register(ClientError, ClientErrorFormatter())
        with self.assertRaises(HandlerError):
            mock_env.run_and_get_result(spider.crawl(Request.of("http://localhost:5000/test_extract")))
        with self.assertRaises(ConnectionError):
            mock_env.run_and_get_result(spider.crawl(Request.of("no exist")))
        with self.assertRaises(ResponseError):
            mock_env.run_and_get_result(spider.crawl(Request.of("http://localhost:5000/error")))


if __name__ == "__main__":
    unittest.main()
