from easy_spider import async_env, AsyncSpider, HTMLResponse


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-list__item a")
        print([title.text for title in titles])


async_env.run(MySpider())

