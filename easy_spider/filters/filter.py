from abc import ABC
from easy_spider.network.request import Request
import re
from typing import List, Any


class Filter(ABC):

    def accept(self, value: Any) -> bool: pass

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

    def accept(self, value: Any) -> bool:
        return not self.filter.accept(value)


class CustomFilter(Filter):
    def __init__(self, filter_func):
        super().__init__()
        self._filter_func = filter_func

    def accept(self, value: Any) -> bool:
        return self._filter_func(value)


class RegexFilter(Filter):
    def __init__(self, re_expr):
        self._re_expr = re.compile(re_expr)

    def accept(self, string: str) -> bool:
        return bool(self._re_expr.match(string))


class URLFilter(Filter):
    def __init__(self, filter):
        self.filter = filter

    def accept(self, request: Request) -> bool:
        return self.filter.accept(request.url)


class AndChainFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters: List[Filter] = list(filters)

    def accept(self, value: Any) -> bool:
        return all([f.accept(value) for f in self._filters])

    def __add__(self, other):
        self._filters.append(other)
        return self

    def __sub__(self, other):
        self._filters.append(NotFilter(other))
        return self


class OrChainFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters: List[Filter] = list(filters)

    def accept(self, value: Any) -> bool:
        return any([f.accept(value) for f in self._filters])

    def __or__(self, other):
        self._filters.append(other)
        return self
