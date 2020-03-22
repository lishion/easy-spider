from easy_spider import async_env, RecoverableSpider, Request, HTMLResponse
from easy_spider.filters.build_in import GenerationFilter, URLRegFilter, BloomFilter, HashFilter


class MySpider(RecoverableSpider):

    def __init__(self):
        super().__init__()
        self.start_targets = ["https://github.blog/"]
        self.filter = URLRegFilter(r"^https://github.blog/page/\d+/$")
        self.num_threads = 4
        self.name = "github_task"

    def handle(self, response: HTMLResponse):
        print(response.bs.title.text)
        yield from super().handle(response)


if __name__ == "__main__":
    async_env.run(MySpider())
