import unittest
from easy_spider.error.known_error import *
from asyncio import TimeoutError
from aiohttp.client_exceptions import ClientConnectionError
from easy_spider.error.error_formatter import ClientErrorFormatter, DefaultErrorFormatter
from easy_spider.error.error_handler import handler_error, client_error, forward


@forward(to=handler_error)
def handler():
    raise ValueError("输入错误")


@forward(to=client_error)
def do_request():
    raise TimeoutError()


class TestExceptionFormatter(unittest.TestCase):

    def test_formatter(self):
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


if __name__ == "__main__":
    unittest.main()
