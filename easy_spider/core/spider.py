from easy_spider.network.request import Request
from easy_spider.network.client import AsyncClient
from easy_spider.network.response import Response, HTMLResponse
from easy_spider.extractors.extractor import SimpleBSExtractor
from easy_spider.core.recoverable import Recoverable
from easy_spider.error.error_handler import forward, handler_error
from easy_spider.middlewares.build_in import ChainMiddleware, ExtractorFilterMiddleware, FilterMiddleware, \
    GenerationMiddleware, SetAttrMiddleware
from easy_spider import tool
from abc import ABC, abstractmethod
from easy_spider.filters.build_in import Filter, html_filter, all_pass_filter, HashFilter, CrawledFilter
from typing import Iterable
from os.path import join


class Spider(ABC):

    def __init__(self):
        self._start_targets = []
        self.num_threads = 1
        self.num_of_spill = 10000
        self._filter = html_filter
        self.extractor = SimpleBSExtractor()
        self._crawled_filter = HashFilter()
        self.init()
        self._middlewares = self.middlewares()
        self._start_targets = list(self._middlewares.transform(self._start_targets, None))

    def init(self):
        pass

    def middlewares(self):
        return ChainMiddleware(GenerationMiddleware(),  # 设置请求为第 n 代
                               ExtractorFilterMiddleware(self.filter),  # 请求提取过滤器
                               FilterMiddleware(self.crawled_filter),  # 历史请求过滤器
                               SetAttrMiddleware(self))  # 设置请求默认参数

    @property
    def start_targets(self):
        return self._start_targets

    @start_targets.setter
    def start_targets(self, targets):
        self._start_targets = list(self.from_url_or_request_iter(targets))

    @property
    def crawled_filter(self):
        return self._crawled_filter

    @crawled_filter.setter
    def crawled_filter(self, filter):
        if filter and not isinstance(filter, CrawledFilter):
            raise TypeError("crawled_filter must be a CrawledFilter, got a {}".format(filter.__class__.__name__))
        self._crawled_filter = filter

    @property
    def filter(self): return self._filter

    @filter.setter
    def filter(self, filter):
        self._filter = filter or all_pass_filter

    @staticmethod
    def from_url_or_request(url: str):
        return Request.of(url)

    def from_url_or_request_iter(self, urls: Iterable[str]):
        yield from (self.from_url_or_request(url) for url in urls)

    @staticmethod
    def _nothing():
        return range(0)

    @abstractmethod
    def crawl(self, request: Request):
        pass


# class MultiThreadSpider(Spider, SimpleClient):
#
#     def __init__(self, handlers):
#         super().__init__(handlers)
#         self.start_requests = []
#
#     def crawl(self, request: Request):
#         response = self.do_request(request)  # 发送请求
#         return request.handler(response)


class AsyncSpider(Spider, AsyncClient):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def handle(self, response: Response):
        """
        从 Response 中提取 Request，提取的 Request 将会设置默认参数
        """
        if isinstance(response, HTMLResponse):
            yield from self.from_url_or_request_iter(self.extractor.extract(response))
        else:
            yield from self._nothing()

    async def crawl(self, request: Request):
        """
        爬虫主要逻辑
        """
        response = await self.do_request(request)
        handler = forward(to=handler_error)(request.handler or self.handle)  # 包装错误处理
        request_like_iter = handler(response)
        if not request_like_iter:
            return self._nothing()
        return self._middlewares.transform(request_like_iter, response)


class RecoverableSpider(AsyncSpider, Recoverable, ABC):

    def __init__(self):
        self.name = None
        self.auto_save_frequency = 1000
        super().__init__()

    def stash(self, resource):
        self._crawled_filter.stash(resource)

    def recover(self, resource):
        self._crawled_filter.recover(resource)
        self._middlewares = self.middlewares()

    def can_recover(self, resource):
        return self._crawled_filter.can_recover(resource)
