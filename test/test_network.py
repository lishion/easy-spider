import unittest
from test.tools import test_page
from aioresponses import CallbackResult
from easy_spider.core.queue import RecoverableRequestQueue, \
    SpillRequestQueueProxy, RecoverableSpillRequestQueueProxy, SimpleRequestQueue, get_queue_for_spider
from easy_spider.network.request import Request
from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.tool import EXE_PATH
import re
from test.mock_env import env, get
from os.path import join


class ASpider(AsyncSpider):
    def handle(self, response):
        pass


class RSpider(RecoverableSpider):
    def handle(self, response):
        pass


class TestNetWork(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        env.mocked.get(re.compile(r"^http://localhost:5000/test_encoding.*$"),
                       content_type="text/html",
                       callback=TestNetWork.handler,
                       repeat=True)
        env.mocked.get("http://localhost:5000/test_request",
                       body='ok',
                       content_type="text/html",
                       repeat=True)

    @staticmethod
    def handler(url, **_):
        charset = url.query.get("charset", '')
        content_type = "text/html;charset={}".format(charset)
        return CallbackResult(
            body=test_page,
            content_type=content_type,
            status=200
        )

    def test_request(self):
        resp = get("http://localhost:5000/test_request")
        self.assertEqual(resp.text, "ok")

        resp = get("http://localhost:5000/test_request")
        self.assertEqual(resp.text, "ok")

    def test_set_encoding(self):
        text_response = get("http://localhost:5000/test_encoding")
        text_response.encoding = "utf-8"
        self.assertEqual(text_response.encoding, "utf-8")

    def test_infer_encoding(self):
        text_response = get("http://localhost:5000/test_encoding?charset=gb2312")
        self.assertEqual(text_response.encoding, 'gb18030')

        text_response = get("http://localhost:5000/test_encoding?charset=gbk")
        self.assertEqual(text_response.encoding, 'gb18030')

        text_response = get("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertEqual(text_response.encoding, 'utf-8')

    def test_decode(self):
        # 测试编码错误的情况，此情况无法正常解码
        text_response = get("http://localhost:5000/test_encoding?charset=gb2312")
        self.assertNotIn("世界", text_response.text)

        # 测试编码正确的情况
        text_response = get("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertIn("世界", text_response.text)

        # 测试编码不存在的情况
        text_response = get("http://localhost:5000/test_encoding")
        self.assertIn("世界", text_response.text)

        # 测试错误编码，但采用自动推断解码的情况
        text_response = get("http://localhost:5000/test_encoding?charset=gb2312")
        text_response.encoding = None  # 从内容自动推断 encoding
        self.assertIn("世界", text_response.text)

        # 测试给定不存在编码的情况
        text_response = get("http://localhost:5000/test_encoding?charset=ggg")
        self.assertIn("世界", text_response.text)
        text_response.encoding = "ggg"
        self.assertIn("世界", text_response.text)

    def test_cache(self):
        html_response = get("http://localhost:5000/test_encoding?charset=utf-8")
        self.assertIs(html_response.bs, html_response.bs)

    def test_ensure_request_callable(self):
        r = Request("test")
        with self.assertRaises(TypeError):
            r.handler = 1
        r.handler = lambda x: x

    def test_build_request(self):
        r = Request.of("http://test")
        self.assertEqual(r.url, "http://test")
        r1 = Request.of(r)
        self.assertIs(r1, r)
        with self.assertRaises(TypeError):
            Request.of(1)

    def test_recover_queue(self):
        queue = RecoverableRequestQueue()
        queue.put(Request.of("1"))
        queue.put(Request.of("2"))
        queue.put(Request.of("3"))
        queue.stash(EXE_PATH)
        del queue

        recovered_queue = RecoverableRequestQueue()
        recovered_queue.recover(EXE_PATH)
        self.assertFalse(recovered_queue.empty())
        i = 1
        while not recovered_queue.empty():
            request = recovered_queue.get()
            self.assertEqual(request.url, str(i))
            i += 1

    def test_spill_queue(self):
        # queue = RecoverableRequestQueue()
        # queue_proxy = SpillRequestQueueProxy(queue, 10)
        numbers = list(range(52))
        # queue_proxy.put_many(numbers)
        # others = []
        # self.assertEqual(len(queue_proxy), 52)
        # while not queue_proxy.empty():
        #     others.append(queue_proxy.get())
        # self.assertEqual(numbers, others)

        queue = RecoverableRequestQueue()
        queue_proxy = RecoverableSpillRequestQueueProxy(queue, 10)
        queue_proxy.put_many(numbers)
        queue_proxy.stash(EXE_PATH)
        del queue_proxy

        stashed_queue_proxy = RecoverableSpillRequestQueueProxy(queue, 10)
        stashed_queue_proxy.recover(EXE_PATH)
        others = []
        self.assertEqual(len(stashed_queue_proxy), 52)
        while not stashed_queue_proxy.empty():
            others.append(stashed_queue_proxy.get())
        self.assertEqual(numbers, others)

    def test_get_queue(self):
        aspider = ASpider()
        rspider = RSpider()
        aspider.num_of_spill = 0
        rspider.num_of_spill = 0
        self.assertEqual(get_queue_for_spider(aspider).__class__, SimpleRequestQueue)
        self.assertEqual(get_queue_for_spider(rspider).__class__, RecoverableRequestQueue)
        aspider.num_of_spill = 10000
        rspider.num_of_spill = 10000
        self.assertEqual(get_queue_for_spider(aspider).__class__, SpillRequestQueueProxy)
        self.assertEqual(get_queue_for_spider(rspider).__class__, RecoverableSpillRequestQueueProxy)
        with self.assertRaises(TypeError):
            get_queue_for_spider(1)


if __name__ == '__main__':
    unittest.main()
