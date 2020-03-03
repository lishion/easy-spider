import unittest
import requests
from spider.response import HTMLResponse


class TestResponse(unittest.TestCase):

    @staticmethod
    def get_text_response(url):
        r = requests.get(url)
        text_response = HTMLResponse(r.content, r.url, r.headers)
        return text_response

    def test_set_encoding(self):
        text_response = self.get_text_response("http://localhost:5000/test_encoding")
        text_response.encoding = "utf-8"
        self.assertEqual(text_response.encoding, "utf-8")

    def test_infer_encoding(self):
        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=gbk")
        self.assertEqual(text_response.encoding, 'gb18030')

        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=gb2312")
        self.assertEqual(text_response.encoding, 'gb18030')

        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertEqual(text_response.encoding, 'utf-8')

    def test_decode(self):
        # 测试编码错误的情况，此情况无法正常解码
        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=gb2312")
        self.assertNotIn("世界", text_response.text)

        # 测试编码正确的情况
        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertIn("世界", text_response.text)

        # 测试编码不存在的情况
        text_response = self.get_text_response("http://localhost:5000/test_encoding")
        self.assertIn("世界", text_response.text)

        # 测试错误编码，但采用自动推断解码的情况
        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=gb2312")
        text_response.encoding = None  # 从内容自动推断 encoding
        self.assertIn("世界", text_response.text)

        # 测试给定不存在编码的情况
        text_response = self.get_text_response("http://localhost:5000/test_encoding?charset=ggg")
        self.assertIn("世界", text_response.text)
        text_response.encoding = "ggg"
        self.assertIn("世界", text_response.text)

    def test_cache(self):
        html_response = self.get_text_response("http://localhost:5000/test_encoding?charset=utf-8", HTMLResponse)
        self.assertIs(html_response.bs, html_response.bs)


if __name__ == '__main__':
    unittest.main()
