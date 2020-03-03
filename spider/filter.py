from abc import ABC, abstractmethod
from spider.resource import Resource
import re
from typing import List, Tuple
from .tool import get_extension


class Filter(ABC):

    def accept(self, resource: Resource) -> bool: pass

    def __neg__(self):
        return NotFilter(self)

    def __add__(self, other):
        return AndChainFilter(self, other)

    def __or__(self, other):
        return OrChainFilter(self, other)

    def __sub__(self, other):
        return AndChainFilter(self, NotFilter(other))


class URLFilter(Filter):

    def __init__(self, filter):
        super().__init__()
        self.filter = filter

    def accept(self, resource: Resource) -> bool:
        return self.accept(resource.uri)


class NotFilter(Filter):
    def __init__(self, filter):
        super().__init__()
        self.filter = filter

    def accept(self, resource: Resource) -> bool:
        return not self.filter.accept(resource)


class CustomFilter(Filter):
    def __init__(self, filter_func):
        super().__init__()
        self._filter_func = filter_func

    def accept(self, resource: Resource) -> bool:
        return self._filter_func(resource)


class RegexFilter(Filter):
    def __init__(self, re_expr):
        self._re_expr = re.compile(re_expr)

    def accept(self, resource: Resource) -> bool:
        return bool(self._re_expr.match(resource.uri))


class AndChainFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters: List[Filter] = list(filters)

    def accept(self, resource: Resource) -> bool:
        return all([f.accept(resource) for f in self._filters])

    def __add__(self, other):
        self._filters.append(other)
        return self

    def __sub__(self, other):
        self._filters.append(NotFilter(other))
        return self


class OrChainFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters: List[Filter] = list(filters)

    def accept(self, resource: Resource) -> bool:
        return any([f.accept(resource) for f in self._filters])

    def __or__(self, other):
        self._filters.append(other)
        return self


# 非 html 后缀， 来源于 scrapy
# https://github.com/scrapy/scrapy/blob/master/scrapy/linkextractors/__init__.py
IGNORED_EXTENSIONS = {
    # archives
    '7z', '7zip', 'bz2', 'rar', 'tar', 'tar.gz', 'xz', 'zip',

    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg', 'cdr', 'ico',

    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a', 'm4v', 'flv', 'webm',

    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
    'odp',

    # other
    'css', 'pdf', 'exe', 'bin', 'rss', 'dmg', 'iso', 'apk'
}

static_filter = CustomFilter(lambda resource: get_extension(resource.uri) in IGNORED_EXTENSIONS)
url_filter = RegexFilter(r"^https?:\/{2}[^\s]*?(\?.*)?$")
html_filter = url_filter - static_filter
