import unittest
from spider import SpiderTask, AsyncSpiderTask
from spider.filter import html_filter
from spider.response import HTMLResponse

spider_task = AsyncSpiderTask(
    start_urls=["http://localhost:5000/test_extract"],
    extractor_filter=html_filter
)


@spider_task.handler(name="test")
def handler(response: HTMLResponse):
    print(response.bs.select("title"))


class TestCore(unittest.TestCase):
    def test_core(self):
        spider_task.run(4)


if __name__ == '__main__':
    unittest.main()
