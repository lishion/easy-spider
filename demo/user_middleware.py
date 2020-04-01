from typing import Iterable, Optional
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse, Response
from easy_spider.middlewares.build_in import RequestMiddleware, ChainMiddleware
from easy_spider.tool import get_abs_path
from easy_spider import GenerationFilter
from os.path import join


class LoadFileMiddleware(RequestMiddleware):

    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        if not response:  # 如果为初始请求，则从文件中构造 urls
            url = list(requests)[0].url
            with open(join(get_abs_path(__file__), url), encoding='utf-8') as fd:
                for line in fd.readlines():
                    yield Request.of(line.strip("\n"))
        else:  # 否则不做任何事情
            yield from requests


class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["urls.txt"]
        self.filter = self.filter + GenerationFilter(max_generation=3)

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-list__item a")
        print([title.text for title in titles])

    def middlewares(self):
        return ChainMiddleware(LoadFileMiddleware()).extend(super().middlewares())


async_env.run(MySpider())
