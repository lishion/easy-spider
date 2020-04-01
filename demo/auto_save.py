from easy_spider import async_env, Request, HTMLResponse
from easy_spider.filters.build_in import GenerationFilter, URLRegFilter, BloomFilter, HashFilter
from easy_spider.core.spider import RecoverableSpider


class MySpider(RecoverableSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        self.filter = URLRegFilter(r"^https://github.blog/page/\d+/$") \
                      + GenerationFilter(max_generation=3)
        self.name = "github_task"
        self.auto_save_frequency = 1
        self.num_threads = 4

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-item__title a")
        print([title.text for title in titles])
        yield from super().handle(response)

print(MySpider().name)

async_env.run(MySpider())