from easy_spider.filters.build_in import *
from easy_spider.network.request import Request
import unittest


class TestFilter(unittest.TestCase):

    def test_reg_filter(self):
        f = RegexFilter(r"http://")
        self.assertTrue(f.accept("http://www.baidu.com"))

    def assert_true(self, r, url):
        self.assertTrue(r.accept(url))

    def assert_false(self, r, url):
        self.assertFalse(r.accept(url))

    def test_and_op(self):
        r = RegexFilter("") + RegexFilter("") + RegexFilter("")
        self.assertEqual(type(r), AndChainFilter)

    def test_or_op(self):
        r = RegexFilter("") | RegexFilter("") | RegexFilter("")
        self.assertEqual(type(r), OrChainFilter)

    def test_and_filter(self):
        r = RegexFilter("http://") + RegexFilter(".*?test")
        self.assert_false(r, "http://www.baidu.com")
        self.assert_true(r, "http://www.test.com")

    def test_or_filter(self):
        r = RegexFilter("http://") | RegexFilter("https://")
        self.assert_true(r, "http://www.baidu.com")
        self.assert_true(r, "https://www.baidu.com")

    def test_not_filter(self):
        r = -RegexFilter("javascript:")
        self.assert_false(r, "javascript:")

    def test_and_not_filter(self):
        r = RegexFilter(".*") + (-RegexFilter("javascript:"))
        self.assert_true(r, "http://www.baidu.com")
        self.assert_false(r, "javascript:func(1)")

        r = RegexFilter(".*") - RegexFilter("javascript:") - RegexFilter("https://")
        self.assert_true(r, "http://www.baidu.com")
        self.assert_false(r, "https://www.baidu.com")
        self.assert_false(r, "javascript:func(1)")

    def test_html_filter(self):
        self.assert_true(html_filter, "http://www.baidu.com")
        self.assert_true(static_filter, "http://www.baidu.com/a.zip")
        self.assert_false(html_filter, "http://www.baidu.com/a.zip")
        self.assert_false(html_filter, "http://www.baidu.com/b.Mp4")
        self.assert_false(html_filter, "http://www.baidu.com/b.mP3")


if __name__ == '__main__':
    unittest.main()
