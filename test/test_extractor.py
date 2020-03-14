from easy_spider.extractors.extractor import *
import unittest
from test.mock_env import get


class Extractor(unittest.TestCase):

    @staticmethod
    def extract_urls(url):
        extractor = SimpleBSExtractor()
        return list(extractor.extract(get(url)))

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
