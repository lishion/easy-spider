from spider import AsyncSpiderTask
from spider.filter import html_filter
from spider.response import HTMLResponse
from spider.filter import RegexFilter

spider_task = AsyncSpiderTask(
    start_urls=["http://localhost:5000/test_extract"],
    extractor_filter=RegexFilter("^https?://www.go") | RegexFilter("http?://dsafa")
)


@spider_task.handler(name="test")
def handler(response: HTMLResponse):
    print(response.bs.select("title"))


if __name__ == "__main__":
    spider_task.run(4)
