from abc import ABC
from easy_spider.network.request import Request
import re
from typing import List


class Filter(ABC):

    def accept(self, url: str) -> bool: pass

    def __neg__(self):
        return NotFilter(self)

    def __add__(self, other):
        return AndChainFilter(self, other)

    def __or__(self, other):
        return OrChainFilter(self, other)

    def __sub__(self, other):
        return AndChainFilter(self, NotFilter(other))


class NotFilter(Filter):
    def __init__(self, filter):
        super().__init__()
        self.filter = filter

    def accept(self, url: str) -> bool:
        return not self.filter.accept(url)


class CustomFilter(Filter):
    def __init__(self, filter_func):
        super().__init__()
        self._filter_func = filter_func

    def accept(self, url: str) -> bool:
        return self._filter_func(url)


class RegexFilter(Filter):
    def __init__(self, re_expr):
        self._re_expr = re.compile(re_expr)

    def accept(self, url: str) -> bool:
        return bool(self._re_expr.match(url))


class AndChainFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters: List[Filter] = list(filters)

    def accept(self, url: str) -> bool:
        return all([f.accept(url) for f in self._filters])

    def __add__(self, other):
        self._filters.append(other)
        return self

    def __sub__(self, other):
        self._filters.append(NotFilter(other))
        return self


class OrChainFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters: List[Filter] = list(filters)

    def accept(self, url: str) -> bool:
        return any([f.accept(url) for f in self._filters])

    def __or__(self, other):
        self._filters.append(other)
        return self
