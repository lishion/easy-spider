from easy_spider.filters.filter import *
from easy_spider.tool import get_extension


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
    'css', 'pdf', 'exe', 'bin', 'rss', 'dmg', 'iso', 'apk', 'js'
}

static_filter = CustomFilter(lambda url: get_extension(url) in IGNORED_EXTENSIONS)
url_filter = RegexFilter(r"^https?:\/{2}[^\s]*?(\?.*)?$")
html_filter = url_filter - static_filter
all_pass_filter = CustomFilter(lambda _: True)
all_reject_filter = CustomFilter(lambda _: False)


# class BloomFilterWrapper(Filter):
#     """
#     布隆过滤器， 可以依赖于其他过滤器的结果
#     """
#     def __init__(self, max_elements, error_rate, pre_filter: Filter = None):
#         self._history_filter = BloomFilter(max_elements, error_rate)
#         self._pre_filter = pre_filter
#
#     def accept(self, request: Request) -> bool:
#         this_filter_accept = request.uri not in self._history_filter
#         pre_filter_accept = self._pre_filter.accept(request) if self._pre_filter else True
#         accept = this_filter_accept and pre_filter_accept
#         accept and self._history_filter.add(request.uri)  # 如果最终的结果为 True， 则添加到 history_filter 中
#         return accept
