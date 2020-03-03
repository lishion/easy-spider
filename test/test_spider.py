import unittest
from spider import *
from spider.task import SimpleTaskQueen
from spider.response import HTMLResponse
from spider.extractor import SimpleBSExtractor
from spider.request import SimpleRequest
from spider.spider import Spider
from spider.filter import html_filter, RegexFilter
from spider.wrapper import handler
from spider.core import Job

@handler(filter=-RegexFilter("^.*?/a.html$"), name="handler1")
def handle(response: HTMLResponse):
    print(response.bs.select("title"))


@handler(filter=RegexFilter("^.*?/a.html$"), name="handler2")
def handle2(response: HTMLResponse):
    print("handler2" + str(response.bs.select("title")[0]))


class TestSpider(unittest.TestCase):
    def test_spider(self):
        context = Context(
            [handle, handle2],
            SimpleBSExtractor(html_filter),
            SimpleRequest()
        )
        spider = Spider(context)
        job = Job(["http://localhost:5000/test_extract"], spider, SimpleTaskQueen())
        job.start()


if __name__ == '__main__':
    unittest.main()
