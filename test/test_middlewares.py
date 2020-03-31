import unittest
from easy_spider.filters.build_in import *
from easy_spider.middlewares.build_in import *


class A:
    def __init__(self):
        self.method = "POST"


class MockResponse:
    def __init__(self):
        self.request = Request("test", generation=0)


class TestMiddlewares(unittest.TestCase):

    def test_middlewares(self):
        requests = [Request.of("http://www.test"), Request.of("http://a.test")]
        filter_mw = ExtractorFilterMiddleware(URLRegFilter("^https?://www\.test"))
        history_wm = FilterMiddleware(HashFilter())
        copy_wm = SetAttrMiddleware(A())
        gen_wm = GenerationMiddleware()
        wms = ChainMiddleware(gen_wm, filter_mw, history_wm, copy_wm)
        requests_transformed = list(wms.transform(requests, None))
        self.assertEqual(len(list(requests_transformed)), 2)
        self.assertTrue(all(map(lambda r: r.generation == 0, requests_transformed)))
        self.assertTrue(all(map(lambda r: r.method == "POST", requests_transformed)))
        requests_transformed = list(wms.transform(requests, None))
        self.assertEqual(len(list(requests_transformed)), 0)

        filter_mw = ExtractorFilterMiddleware(URLRegFilter("^https?://www\.test"))
        history_wm = FilterMiddleware(HashFilter())
        copy_wm = SetAttrMiddleware(A())
        gen_wm = GenerationMiddleware()
        wms = ChainMiddleware(gen_wm, filter_mw, history_wm, copy_wm)
        requests_transformed = list(wms.transform(requests, MockResponse()))
        self.assertEqual(len(requests_transformed), 1)
        self.assertTrue(all(map(lambda r: r.generation == 1, requests_transformed)))
        self.assertTrue(all(map(lambda r: r.method == "POST", requests_transformed)))


if __name__ == "__main__":
    unittest.main()
