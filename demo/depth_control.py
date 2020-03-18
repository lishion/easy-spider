from easy_spider import async_env, AsyncSpider, Request, HTMLResponse
from easy_spider.filters.build_in import GenerationFilter, URLRegFilter, BloomFilter, HashFilter


class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.start_targets = ["https://github.blog/"]
        self.filter = URLRegFilter(r"^https://github.blog/page/\d+/$") \
                      + GenerationFilter(max_generation=3)

        self.num_threads = 4

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-item__title a")
        print([title.text for title in titles])
        yield from super().handle(response)


async_env.run(MySpider())
