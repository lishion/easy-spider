from easy_spider import async_env, AsyncSpider, Request, HTMLResponse


class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        return [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]


async_env.run(MySpider())

