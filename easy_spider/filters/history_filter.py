from abc import ABC, abstractmethod
from easy_spider.filters.filter import DependenceFilter
from typing import Any, List
from easy_spider.network.request import Request
from bloom_filter import BloomFilter as _BloomFilter
from easy_spider.core.recoverable import FileBasedRecoverable


class CrawledFilter(ABC):
    """
        已爬取过滤器， 依赖于其他过滤器的结果
        pre_filter: 前置过滤器，已爬取过滤器将依赖于前置过滤器的返回结果
        若已爬取过滤器以及前置过滤器都返回 True 则记录到已爬取过滤器，并返回 True
        否则返回 False
    """

    @abstractmethod
    def contains(self, request: Request) -> bool: pass

    @abstractmethod
    def add(self, request: Request): pass

    def accept(self, request: Request) -> bool:
        history_filter_accept = not self.contains(request)
        history_filter_accept and self.add(request)  # 如果不存在于布隆过滤器中，则记录
        return history_filter_accept

    @abstractmethod
    def clear(self): pass


class BloomFilter(CrawledFilter, FileBasedRecoverable):

    def stash_attr_names(self) -> List[str]:
        return ["_history_filter"]

    def __init__(self, max_elements, error_rate):
        CrawledFilter.__init__(self)
        self._max_elements = max_elements
        self._error_rate = error_rate
        self._history_filter = _BloomFilter(max_elements, error_rate)
        FileBasedRecoverable.__init__(self)

    def contains(self, request: Request):
        return request.url in self._history_filter

    def add(self, request: Request):
        self._history_filter.add(request.url)

    def clear(self):
        self._history_filter = _BloomFilter(self._max_elements, self._error_rate)


class HashFilter(CrawledFilter, FileBasedRecoverable):

    def __init__(self):
        self._crawled_urls = set()
        CrawledFilter.__init__(self)
        FileBasedRecoverable.__init__(self)

    def stash_attr_names(self) -> List[str]:
        return ["_crawled_urls"]

    def contains(self, request: Request) -> bool:
        return request.url in self._crawled_urls

    def add(self, request: Request):
        self._crawled_urls.add(request.url)

    def clear(self):
        self._crawled_urls.clear()
