import unittest
from test.tools import test_page
from test.net_mock import NetMockTestCase
from aioresponses import CallbackResult
from easy_spider.network.request import Request
import re


class TestResponse(NetMockTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.mocked.get(re.compile(r"^http://localhost:5000/test_encoding.*$"), content_type="text/html", callback=TestResponse.handler, repeat=True)
        cls.mocked.get("http://localhost:5000/test_request", body='ok', content_type="text/html", repeat=True)

    @staticmethod
    def handler(url, **_):
        charset = url.query.get("charset", '')
        content_type = f"text/html;charset={charset}"
        return CallbackResult(
            body=test_page,
            content_type=content_type,
            status=200
        )

    async def fetch(self, url):
        super().prepare()
        return await TestResponse.client.do_request(Request(url))

    def get_response(self, url):
        return self.run_and_get_result(self.fetch(url))

    def test_request(self):
        resp = self.get_response("http://localhost:5000/test_request")
        self.assertEqual(resp.text, "ok")

        resp = self.get_response("http://localhost:5000/test_request")
        self.assertEqual(resp.text, "ok")

    def test_set_encoding(self):
        text_response = self.get_response("http://localhost:5000/test_encoding")
        text_response.encoding = "utf-8"
        self.assertEqual(text_response.encoding, "utf-8")

    def test_infer_encoding(self):
        text_response = self.get_response("http://localhost:5000/test_encoding?charset=gb2312")
        self.assertEqual(text_response.encoding, 'gb18030')

        text_response = self.get_response("http://localhost:5000/test_encoding?charset=gbk")
        self.assertEqual(text_response.encoding, 'gb18030')

        text_response = self.get_response("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertEqual(text_response.encoding, 'utf-8')

    def test_decode(self):
        # 测试编码错误的情况，此情况无法正常解码
        text_response = self.get_response("http://localhost:5000/test_encoding?charset=gb2312")
        self.assertNotIn("世界", text_response.text)

        # 测试编码正确的情况
        text_response = self.get_response("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertIn("世界", text_response.text)

        # 测试编码不存在的情况
        text_response = self.get_response("http://localhost:5000/test_encoding")
        self.assertIn("世界", text_response.text)

        # 测试错误编码，但采用自动推断解码的情况
        text_response = self.get_response("http://localhost:5000/test_encoding?charset=gb2312")
        text_response.encoding = None  # 从内容自动推断 encoding
        self.assertIn("世界", text_response.text)

        # 测试给定不存在编码的情况
        text_response = self.get_response("http://localhost:5000/test_encoding?charset=ggg")
        self.assertIn("世界", text_response.text)
        text_response.encoding = "ggg"
        self.assertIn("世界", text_response.text)

    def test_cache(self):
        html_response = self.get_response("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertIs(html_response.bs, html_response.bs)

    def test_ensure_request_callable(self):
        r = Request("test")
        with self.assertRaises(TypeError):
            r.handler = 1
        r.handler = lambda x: x


if __name__ == '__main__':
    unittest.main()
