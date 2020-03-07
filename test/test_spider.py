import unittest
from spider import *
from spider.resource import SimpleResourceQueue, Resource
from spider.response import HTMLResponse
from spider.extractor import SimpleBSExtractor
from spider.request import SimpleRequest, AsyncRequest
from spider.spider import Spider, AsyncSpider
from spider.filter import html_filter, RegexFilter
from spider.wrapper import handler
from asyncio import get_event_loop
from aiohttp import ClientSession

@handler(filter=-RegexFilter("^.*?/a.html$"), name="handler1")
def handle(response: HTMLResponse):
    print(response.bs.select("title"))


@handler(filter=RegexFilter("^.*?/a.html$"), name="handler2")
def handle2(response: HTMLResponse):
    print("handler2" + str(response.bs.select("title")[0]))


class TestSpider(unittest.TestCase):
    # def test_spider(self):
    #     context = Context(
    #         [handle, handle2],
    #         SimpleBSExtractor(html_filter),
    #         SimpleRequest()
    #     )
    #     spider = Spider(context)
    #     job = Job(["http://localhost:5000/test_extract"], spider, SimpleResourceQueue())
    #     job.start()

    async def async_spider(self):
        r = Resource("http://localhost:5000/test_extract", "http://localhost:5000/test_extract")
        async with ClientSession() as session:
            context = Context(
                [handle, handle2],
                SimpleBSExtractor(html_filter),
                AsyncRequest(session)
            )
            await AsyncSpider(context).crawl(r)

    def test_async_spider(self):
        loop = get_event_loop()
        loop.run_until_complete(self.async_spider())

    def test_simple_spider(self):
        r = Resource("http://localhost:5000/test_extract", "http://localhost:5000/test_extract")
        context = Context(
            [handle, handle2],
            SimpleBSExtractor(html_filter),
            SimpleRequest()
        )
        Spider(context).crawl(r)

if __name__ == '__main__':
    unittest.main()
