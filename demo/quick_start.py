from easy_spider import async_env, AsyncSpider, HTMLResponse


class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-list__item a")
        print([title.text for title in titles])


async_env.run(MySpider())

