from easy_spider import async_env, AsyncSpider, Request, HTMLResponse


class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        self.cookies = {"key": "value"}  # 用于设置默认请求参数

    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        yield from self.from_url_or_request_iter(urls)  # 所有请求的 cookies 都将设置与 self.cookies 相同


async_env.run(MySpider())
