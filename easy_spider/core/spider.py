from easy_spider.network.request import Request
from easy_spider.network.client import AsyncClient
from easy_spider.network.response import Response, HTMLResponse
from easy_spider.extractors.extractor import SimpleBSExtractor
from easy_spider.core.recoverable import FileBasedRecoverable
from easy_spider import tool
from abc import ABC, abstractmethod
from easy_spider.filters.build_in import Filter, html_filter, all_pass_filter, HashFilter, CrawledFilter
from typing import Iterable
from os.path import join


class Spider(ABC):

    def __init__(self):
        self._start_targets = []
        self.num_threads = 1
        self._filter = html_filter
        self.extractor = SimpleBSExtractor()
        self._crawled_filter = HashFilter()

    @property
    def start_targets(self):
        return self._start_targets

    @start_targets.setter
    def start_targets(self, targets):
        self._start_targets = list(self.from_url_iter(targets))
        self._crawled_filter.clear()  # 首先清空 _crawled_filter 避免重复调用导致重复设置
        for request in self.start_targets:  # 则需将初始 requests 放入 crawled_filer
            self._crawled_filter.contains(request) or self._crawled_filter.add(request)

    @property
    def crawled_filter(self):
        return self._crawled_filter

    @crawled_filter.setter
    def crawled_filter(self, filter):
        if filter and not isinstance(filter, CrawledFilter):
            raise TypeError("crawled_filter must be a CrawledFilter, got a {}".format(filter.__class__.__name__))
        self._crawled_filter = filter
        for request in self.start_targets:  # 用户更改默认 crawled_filer, 需将初始 requests 放入其中
            self._crawled_filter.contains(request) or self._crawled_filter.add(request)

    @property
    def filter(self): return self._filter

    @filter.setter
    def filter(self, filter):
        self._filter = filter or all_pass_filter

    def _get_whole_filter(self) -> Filter:
        """
            将 self.filter 与 self.crawled_filter 组成最终的 filter
        """
        filter = self.filter
        if self.crawled_filter:
            self.crawled_filter.pre_filter = self.filter   # 如果 crawled_filter 不为空，则需要设置其 pre_filter
            filter = self.crawled_filter  # 并将 crawled_filter 设置为最终的 filter
        return filter

    @staticmethod
    def _process_request_after_handler(request_like_iter, source_request):
        """
            在 handler 之后对 request 进行进一步处理
        """
        for request_like in request_like_iter:
            new_request = Request.of(request_like)
            new_request.generation = source_request.generation + 1
            yield new_request

    def _set_default_request_param(self, request):
        """
            若 self 中存在与 request 相同名称的属性，则将其值复制给 request
        """
        for attr in tool.get_public_attr(request):
            hasattr(self, attr) and tool.copy_attr(attr, self, request)
        return request

    def from_url(self, url: str, use_default_params=True):
        """
            先根据 request_like 对象生成 request 对象，
            若 use_default_params 为 True，则使用默认值覆盖 request 中的值，
            否则直接方法 request 对象
        """
        request = Request.of(url)
        if use_default_params:
            request = self._set_default_request_param(request)
        return request

    def from_url_iter(self, urls: Iterable[str], use_default_params=True):
        yield from (self.from_url(url, use_default_params) for url in urls)

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
            yield from self.from_url_iter(self.extractor.extract(response))
        else:
            yield from self._nothing()

    async def crawl(self, request: Request):
        """
        爬虫主要逻辑
        """
        response = await self.do_request(request)
        handler = request.handler or self.handle
        request_like_iter = handler(response)
        if not request_like_iter:
            return self._nothing()
        new_requests = self._process_request_after_handler(request_like_iter, request)
        return filter(self._get_whole_filter().accept, new_requests)


class RecoverableSpider(AsyncSpider, FileBasedRecoverable, ABC):

    def __init__(self):
        AsyncSpider.__init__(self)
        FileBasedRecoverable.__init__(self)
        self.name = None

    def stash_attr_names(self):
        return ["_crawled_filter"]
