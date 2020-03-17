# Easy Spider
## quick start
``` python
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse

class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-list__item a")
        print([title.text for title in titles])

async_env.run(MySpider())
```

本例子中爬取了 https://github.blog/ 。其中 `self.start_targets = ["https://github.blog/"]` 设置了初始需要爬取的目标。`handle(self, response: HTMLResponse)` 方法用于处理服务器返回的 `response`，并产生新的需要爬取得目标。因此 `handle` 方法返回值的类型必须为 `iterable`，或  `handle` 方法自身为一个生成器。在 `easy spider` 中，`AsyncSpider` 已经实现了一个从网页中抽取潜在爬取目标的 `handle` 方法，因此如果需要对 https://github.blog/ 上存在的 URL 进行进一步的爬取，可以:

``` python
def handle(self, response: HTMLResponse):
    titles = response.bs.select(".post-list__item a")
    print([title.text for title in titles])
    yield from super().handle(response)
```
`super().handle(response)` 实际上做了两件事:

1.  获取所有 `a` 标签的 `href` 属性，即页面中可点击的 URL
3. 使用默认参数将其组装为 `Request` 对象(关于这两个概念将在后面的章节提到)

*注意 `super().handle(response)`  只是产生了新的请求对象，你仍然需要使用 ` yield from ` 将 `handle` 构造为一个生成器。*

此外，`handler` 返回的所有目标还将使用利用`self.filter`筛选出需要的 URL `easy_spider.filters.build_in` 内置了几种 `filter`:

* RegexFilter: 正则表达式过滤器
* static_filter: 静态文件过滤器
* url_filter: 合法 URL 过滤器
* html_filter: 响应类型为 html 的 URL 过滤器(通过后缀判定，有一定的误判几率)
* all_pass_filter: 全部接收过滤器
* all_reject_filter: 全部拒绝过滤器

`self.filter` 默认为 `html_filter`，如果你不需要，则可以将其设为 `None`  或 `all_pass_filter`。

## 进阶使用

### 构建自己的URL提取方式

采用默认的提取方式或许无法满足你的需求，可以采用自己的方式提取 URL:

``` python
    def handle(self, response: HTMLResponse):
        # do someting
        yield from (response.url_join(a.attrs["href"]) for a in response.bs.select("a"))
```

其中，`response.url_join` 用于将从网页中提取的原始 URL 转换为绝对 URL。例如你正在访问 `http:www.test.com/page1`，其中提取到的 URL 可能为 `link1`。此时使用 `url_join` 将其转换为 `http:www.test.com/page1/link1`。

### 自定义请求参数

虽然在前面的示例中都是直接使用 URL 代表需要进行爬取的目标。但是在 `easy_spider` 中可以使用 `Request` 对象进行更细粒度的控制。例如:

```
    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        for url in urls:
            if url.startswith("you pattern"):
                yield Request(url, cookies={"c1": "v1"})
            else:
                yield Request(url, cookies={"c2": "v2"})
```

`Request` 对象可定义的参数有:

```
method: str = 请求方法 GET|POST|PUT|DELETE 
timeout: int = 超时时间
headers: dict = 请求头，默认{}
cookies: dict = cookies，默认{}
encoding: str = 编码方式，默认utf-8
params: dict = URL参数，默认{}
data: dict = 数据，取决于 data_format
data_format: str = 数据格式 FORM|JSON，若为 FORM 数据通过 application/x-www-form-urlencoded 格式传递，若为 JSON 则通过 application/json。
```
handle 方法返回 str 或 Request 的迭代器都是合法的，`easy spider` 会自动判断，并生成 Request 对象。

### 默认请求参数

很多时候需要定义一系列默认参数，而不是在每个请求中都声明。这样可以使用 `easy spider` 自带的 `from_url(self, url: str, use_default_params=True)` 或 `from_url_iter(self, urls: Iterable[str], use_default_params=True)`方法，该方法会在 `MySpider ` 中寻找与 `Request` 相同名称的属性，并用其构造新请求:

```python
class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.start_targets = ["https://github.blog/"]
        self.cookies = {"key": "value"}  # 用于设置默认请求参数

    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        yield self.from_url(urls)  # 所有请求的 cookies 都将设置与 self.cookies 相同
```

### 自定义处理方法

可以通过设置 `request` 的 `handler` 属性来设置处理该 `Request` 所返回的 `Response`:
```python
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse

class MySpider(AsyncSpider):

    def __init__(self):
        super().__init__()
        self.cookies = {"key": "value"}  # 用于设置默认请求参数
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        for url in urls:
            if url.endswith("jpg"):
                yield Request(url, handler=self.handle_jpg)
            else:
                yield Request(url, handler=self.handle)

    def handle_jpg(self, response):
        # do something
        pass

async_env.run(MySpider())
```


