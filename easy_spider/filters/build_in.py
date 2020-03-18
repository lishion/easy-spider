from easy_spider.filters.filter import *
from easy_spider.tool import get_extension
from easy_spider.filters.history_filter import *

# 非 html 后缀， 来源于 scrapy
# https://github.com/scrapy/scrapy/blob/master/scrapy/linkextractors/__init__.py
_IGNORED_EXTENSIONS = {
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
    'css', 'pdf', 'exe', 'bin', 'rss', 'dmg', 'iso', 'apk', 'js'
}


def URLRegFilter(reg_expr):
    """
    使 RegFilter 直接作用于 Request 对象的 uri
    """
    return URLFilter(RegexFilter(reg_expr))


static_filter = URLFilter(CustomFilter(lambda url: get_extension(url) in _IGNORED_EXTENSIONS))
url_filter = URLRegFilter(r"^https?:\/{2}[^\s]*?(\?.*)?$")
html_filter = url_filter - static_filter
all_pass_filter = CustomFilter(lambda _: True)
all_reject_filter = CustomFilter(lambda _: False)


class GenerationFilter(Filter):
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def accept(self, request: Request) -> bool:
        return request.generation <= self.max_generation
