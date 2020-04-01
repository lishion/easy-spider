from easy_spider import async_env, AsyncSpider, Request, HTMLResponse
from easy_spider import URLRegFilter


class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        self.filter = URLRegFilter(r"^https://github\.blog.+")

    def handle(self, response: HTMLResponse):
        for a in response.bs.select("a"):
            if "href" in a.attrs:
                yield Request.of(response.url_join(a.attrs["href"]))


async_env.run(MySpider())

