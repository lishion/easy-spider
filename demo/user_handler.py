from easy_spider import async_env, AsyncSpider, Request, HTMLResponse


class MySpider(AsyncSpider):

    def init(self):
        self.cookies = {"key": "value"}  # 用于设置默认请求参数
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        for url in urls:
            if url.lower().endswith("jpg"):
                yield Request(url, handler=self.handle_jpg)
            else:
                yield Request(url, handler=self.handle)

    def handle_jpg(self, response):
        # do something
        print("handle jpg with url: {}".format(response.url))
        pass


async_env.run(MySpider())
