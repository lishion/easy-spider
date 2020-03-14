from easy_spider.network.request import Request
from easy_spider.network.client import AsyncClient, SimpleClient
from easy_spider.network.response import Response, HTMLResponse
from easy_spider.extractors.extractor import SimpleBSExtractor
from easy_spider import tool
from abc import ABC, abstractmethod
from easy_spider.filters.build_in import html_filter


class Spider(ABC):

    def __init__(self):
        self._start_requests = []
        self.num_threads = 1
        self.extractor = SimpleBSExtractor()

    @property
    def start_requests(self): return self._start_requests

    @start_requests.setter
    def start_requests(self, requests):
        self._start_requests = [self.set_default_request_param(Request.of(request)) for request in requests]

    def set_default_request_param(self, request):
        """
            若对象中存在与 request 相同名称的属性，则将其复制给 request
        """
        for attr in tool.get_public_attr(request):
            hasattr(self, attr) and tool.copy_attr(attr, self, request)
        return request

    def follow_links(self, urls):
        yield from (self.set_default_request_param(Request.of(url)) for url in urls)

    @staticmethod
    def nothing():
        return range(0)

    @abstractmethod
    def crawl(self, request: Request): pass


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
        self.filter = html_filter

    @abstractmethod
    def handle(self, response: Response):
        if isinstance(response, HTMLResponse):
            yield from filter(lambda request: self.filter.accept(request),
                              self.follow_links(self.extractor.extract(response)))
        else:
            yield from self.nothing()

    async def crawl(self, request: Request):
        response = await self.do_request(request)
        request.handler = request.handler if request.handler else self.handle
        new_requests = request.handler(response)
        if not new_requests:
            return self.nothing()
        return (Request.of(new_request) for new_request in new_requests)
