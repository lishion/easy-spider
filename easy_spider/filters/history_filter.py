from abc import ABC, abstractmethod
from easy_spider.filters.filter import DependenceFilter
from typing import Any
from easy_spider.network.request import Request
from bloom_filter import BloomFilter as _BloomFilter


class CrawledFilter(DependenceFilter, ABC):
    """
        已爬取过滤器， 依赖于其他过滤器的结果
        pre_filter: 前置过滤器，已爬取过滤器将依赖于前置过滤器的返回结果
        若已爬取过滤器以及前置过滤器都返回 True 才记录到布隆过滤器中，并返回 True
        否则返回 False
    """

    @abstractmethod
    def contains(self, request: Request) -> bool: pass

    @abstractmethod
    def add(self, request: Request): pass

    def accept(self, request: Request) -> bool:
        pre_filter_accept = self.pre_filter.accept(request)
        if not pre_filter_accept:  # 如果前置过滤器返回 False 则直接返回 False
            return False
        history_filter_accept = not self.contains(request)
        history_filter_accept and self.add(request)  # 如果不存在于布隆过滤器中，则记录
        return history_filter_accept


class BloomFilter(CrawledFilter):

    def __init__(self, max_elements, error_rate):
        super().__init__()
        self._history_filter = _BloomFilter(max_elements, error_rate)

    def contains(self, request: Request):
        return request.url in self._history_filter

    def add(self, request: Request):
        self._history_filter.add(request.url)


class HashFilter(CrawledFilter):

    def __init__(self):
        super().__init__()
        self._crawled_urls = set()

    def contains(self, request: Request) -> bool:
        return request.url in self._crawled_urls

    def add(self, request: Request):
        self._crawled_urls.add(request.url)
