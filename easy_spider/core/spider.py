from easy_spider.network.request import Request
from easy_spider.network.client import AsyncClient, SimpleClient
from easy_spider.network.response import Response, HTMLResponse
from easy_spider.extractors.extractor import SimpleBSExtractor
from easy_spider import tool
from abc import ABC, abstractmethod
from easy_spider.filters.build_in import html_filter, all_pass_filter
from typing import Iterable


class Spider(ABC):

    def __init__(self):
        self._start_targets = []
        self.num_threads = 1
        self._filter = html_filter
        self.extractor = SimpleBSExtractor()

    @property
    def start_targets(self):
        return self._start_targets

    @start_targets.setter
    def start_targets(self, targets):
        self._start_targets = self.from_url_iter(targets, use_default_params=False)

    @property
    def filter(self): return self._filter

    @filter.setter
    def filter(self, filter):
        self._filter = filter or all_pass_filter

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
        if isinstance(response, HTMLResponse):
            yield from self.from_url_iter(self.extractor.extract(response))
        else:
            yield from self._nothing()

    async def crawl(self, request: Request):
        response = await self.do_request(request)
        request.handler = request.handler if request.handler else self.handle
        new_requests = request.handler(response)
        if not new_requests:
            return self._nothing()
        return filter(lambda r: self.filter.accept(r.uri),
                      (Request.of(new_request) for new_request in new_requests))
