from easy_spider.extractors.extractor import *
import unittest
import requests


class Extractor(unittest.TestCase):

    @staticmethod
    def get_text_response(url):
        r = requests.get(url)
        text_response = HTMLResponse(r.content, r.url, r.headers)
        return text_response

    def extract_urls(self, url):
        extractor = SimpleBSExtractor()
        return list(extractor.extract(self.get_text_response(url)))

    def test_simple_extractor(self):
        urls = self.extract_urls("http://localhost:5000/test_extract")
        self.assertIn("http://localhost:5000/a.html", urls)
        self.assertIn("http://localhost:5000/b/c/d", urls)
        self.assertIn("javascript:func(1)", urls)
        self.assertIn("http://localhost:5000/test.zip", urls)
        self.assertIn("http://localhost:5000/test.Mp4", urls)
        self.assertIn("http://localhost:5000/test.mP3", urls)


if __name__ == "__main__":
    unittest.main()
