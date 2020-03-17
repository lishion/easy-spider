from easy_spider.filters.filter import *
from easy_spider.tool import get_extension
from bloom_filter import BloomFilter

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


class HistoryFilter(Filter):
    """
    布隆过滤器， 依赖于其他过滤器的结果
    pre_filter: 前置过滤器，布隆过滤器将依赖于前置过滤器的返回结果
    若布隆过滤器以及前置过滤器都返回 True 才记录到布隆过滤器中，并返回 True
    否则返回 False
    """
    def __init__(self, pre_filter: Filter, max_elements, error_rate):
        self._history_filter = BloomFilter(max_elements, error_rate)
        self._pre_filter = pre_filter or all_pass_filter

    def accept(self, url: str) -> bool:
        pre_filter_accept = self._pre_filter.accept(url)
        if not pre_filter_accept:  # 如果前置过滤器返回 False 则直接返回 False
            return False
        history_filter_accept = url not in self._history_filter
        history_filter_accept and self._history_filter.add(url)  # 如果不存在于布隆过滤器中，则记录
        return history_filter_accept


def history_filter(pre_filter: Filter, max_elements: int, error_rate: float):
    return HistoryFilter(pre_filter, max_elements, error_rate)
