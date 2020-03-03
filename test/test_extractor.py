from spider.extractor import *
import unittest
import requests
from spider.filter import *


class Extractor(unittest.TestCase):

    @staticmethod
    def get_text_response(url):
        r = requests.get(url)
        text_response = HTMLResponse(r.content, r.url, r.headers)
        return text_response

    def extract_urls(self, filters, url):
        extractor = SimpleBSExtractor(filters)
        tasks = extractor.extract(self.get_text_response(url))
        return [t.resource.uri for t in tasks]

    def test_simple_extractor(self):
        urls = self.extract_urls(html_filter, "http://localhost:5000/test_extract")
        self.assertIn("http://localhost:5000/a.html", urls)
        self.assertIn("http://localhost:5000/b/c/d", urls)
        self.assertNotIn("javascript:func(1)", urls)
        self.assertNotIn("/test.zip", urls)
        self.assertNotIn("/test.Mp4", urls)
        self.assertNotIn("/test.mP3", urls)
