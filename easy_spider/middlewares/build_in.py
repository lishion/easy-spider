from abc import ABC, abstractmethod
from easy_spider.network.request import Request
from easy_spider.network.response import Response
from easy_spider.tool import get_public_attr, copy_attr
from typing import List, Iterable, Optional
from easy_spider.filters.build_in import Filter


class RequestMiddleware(ABC):

    @abstractmethod
    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]: pass


class FilterMiddleware(RequestMiddleware):
    def __init__(self, filter: Filter):
        self._filter = filter

    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        yield from filter(self._filter.accept, requests)


class ExtractorFilterMiddleware(FilterMiddleware):
    def __init__(self, filter: Filter):
        super().__init__(filter)

    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        if not response:  # 如果 response 为空，则说明为初始 requests，不需要进行过滤
            yield from requests
        else:
            yield from super().transform(requests, response)


class GenerationMiddleware(RequestMiddleware):

    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        if response:
            source_request = response.request
            for request in requests:
                request.generation = source_request.generation + 1
                yield request
        else:
            yield from requests


class SetAttrMiddleware(RequestMiddleware):

    def __init__(self, from_instance, attrs=None):
        self._from_instance = from_instance
        self._attrs = attrs

    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        for request in requests:
            for attr in (self._attrs or get_public_attr(request)):  # 如果有指定的 attr 则使用指定的 attr, 否则动态获取
                hasattr(self._from_instance, attr) and copy_attr(attr, self._from_instance, request)
            yield request


class ChainMiddleware(RequestMiddleware):

    def __init__(self, *middlewares: RequestMiddleware):
        self._middlewares: List[RequestMiddleware] = list(middlewares)

    @property
    def middlewares(self): return self._middlewares

    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        r = requests
        for middleware in self._middlewares:
            r = middleware.transform(r, response)
        yield from r

    def extend(self, middleware: 'ChainMiddleware'):
        self._middlewares.extend(middleware.middlewares)
        return self
