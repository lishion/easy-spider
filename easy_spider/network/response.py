from abc import ABC
from urllib.parse import urljoin
from w3lib.encoding import html_to_unicode, http_content_type_encoding
from bs4 import BeautifulSoup
from cached_property import cached_property


class Response(ABC):
    def __init__(self, body, url, headers, request=None):
        self.body = body
        self.url = url
        self.headers = headers
        self.request = request

    def url_join(self, other_url):
        return urljoin(self.url, other_url)


class TextResponse(Response):
    """
        将 requests.response 对象解码为 TextResponse
        首先从 headers["Content-Type"] 中推断编码类型
        若不存在，则使用 w3lib.encoding.http_content_type_encoding 解码并推断编码类型
        w3lib.encoding.http_content_type_encoding 推断编码类型时需要耗费额外计算量
        若已知确定的编码格式，可以直接指定。
        如:
            r.encoding = 'gb2312'
            r.text # 将采用 gb2312 进行解码
        在某些情况，一些网站会给出与网站内容不符合的编码，这时候会导致乱码。此时可以将 r.encoding 设置为 None
        使用自动从网页内容推断编码
            r.encoding = None
            r.text # 自动从网页内容推断编码，乱码概率小，但会引入额外计算量
    """
    def __init__(self, body, url, headers):
        super().__init__(body, url, headers)
        self._encoding = self._infer_encoding_from_content_type()  # 从 Content-Type 中推断编码
        self._text = None

    def _decoding(self):
        charset = f'charset={self._encoding}'
        enc, text = html_to_unicode(charset, self.body)
        self._encoding = enc
        self._text = text

    def _infer_encoding_from_content_type(self):
        content_type = self.headers.get("Content-Type")
        if content_type:
            return http_content_type_encoding(content_type)
        return None

    @property
    def text(self):
        if self._text is None:
            self._decoding()
        return self._text

    @property
    def encoding(self):
        # 如果 Content-Type 从无法推测编码
        # 则使用 w3lib.encoding.http_content_type_encoding
        # 使用详情见: https://w3lib.readthedocs.io/en/latest/w3lib.html
        if self._encoding is None:
            self._decoding()
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding
        self._text = None  # 当用户重设编码时，需要清除 text 属性缓存


class HTMLResponse(TextResponse):

    @cached_property
    def bs(self):
        return BeautifulSoup(self.text, 'lxml')
