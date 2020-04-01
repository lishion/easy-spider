# Easy Spider
## release note 
1.0.13: 添加自动保存功能

1.1.2: 引入中间件处理，优化 easy_spider.core.Spider 中对请求进行处理的逻辑。

## quick start
``` python
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse
    
class MySpider(AsyncSpider):

    def init(self):
        super().__init__()
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-list__item a")
        print([title.text for title in titles])

async_env.run(MySpider())
```

这段代码定义了一个`spider`对象，并爬取了[github-blog](https://github.blog/) 中文章的标题。其中主要包含了`init` 以及 `handle` 两个方法。在`init`方法中可以对爬虫的参数进行设置。例如 `self.start_targets = ["https://github.blog/"]` 设置了初始爬取目标。而 `handle(self, response: HTMLResponse)`  方法主要用于对服务器返回的内容进行处理。`response.bs` 表示一个由返回的网页构造的 [Beautiful Soup4](https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/) 对象，你可以用它来提取需要的内容。

## 发现新链接

`handle` 方法除了处理服务器返回的响应对象[Response](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/network/response.py)以外，还有一个重要的功能则是发现新的链接。在 `easy_spider` 中，一个新的链接需要组装成一个请求对象 [Request](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/network/request.py?tab=files) 。请求对象除了包含需要爬取的链接外，还包含爬取这个链接的参数或`Cookies`等内容，这些内容大部分具有默认值。一个跟随链接的示例为:

``` python
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse

class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        
    def handle(self, response: HTMLResponse):
        for a in response.bs.select("a"):
            if "href" in a.attrs:
                yield Request.of(response.url_join(a.attrs["href"]))
```

`response.url_join` 方法将网页中的相对链接变为绝对链接，例如从 `page/2` 变为 `https://github.blog/2`。`Request.of` 方法利用 `url` 创建具有默认参数的 `Request` 对象。`handle` 方法可以是一个生成器或者也可以直接返回可迭代 `Request` 对象集合。所有 `handle` 产生的新 `Request` 对象都将放入待请求队列中，逐个进行请求。当某个请求完成后，将继续调用 `handle` 方法进行处理。

`easy_spider` 中已经实现了一个简单灵活的发现新链接的方法，你可以直接:

``` python
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse

class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        
    def handle(self, response: HTMLResponse):
        yield from super().handle(response)  # 默认发现新连接的方法
```

发现 `response` 中的所有链接。

## 进阶使用

### 使用过滤器

在默认的情况下，除初始请求外的所有请求都将使用过滤器 [Filter](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/filters/filter.py) 进行过滤。过滤器接收一个参数，并返回布尔值，表示接受或是拒绝这个参数。在定义 `spider` 对象时可以指定 `self.filter`，表示不被该 `filter` 接收的请求都不会放入请求队列中。例如:

```python
class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        self.filter = URLRegFilter(r"^https://github\.blog.+")

    def handle(self, response: HTMLResponse):
        for a in response.bs.select("a"):
            if "href" in a.attrs:
                yield Request.of(response.url_join(a.attrs["href"]))
```

在 `handle` 方法中虽然提取了所有的 URL，但采用 `URLRegFilter` 对其进行了过滤。只有 `URL` 满足 `r"^https://github\.blog.+"` 的请求会被放入队列，否则将被丢弃。在 `easy_spider` 中主要包含**普通过滤器** 以及**去重过滤器**两种类型的过滤器，普通过滤器有如下几种:

- RegexFilter: 正则表达式过滤器
- static_filter: 静态文件过滤器(避免爬取到 jpg|css 等类型文件)
- url_filter: 合法 URL 过滤器
- html_filter: 响应类型为 html 的 URL 过滤器(通过后缀判定，有一定的误判几率)
- all_pass_filter: 全部接收过滤器
- all_reject_filter: 全部拒绝过滤器
- GenerationFilter: 拒绝深度大于某个值的请求

过滤器支持某些运算符操作，例如 `static_filter` 虽然表示接受静态文件，但在如果 `-static_filter`  则变为拒绝静态文件。这里设有两个过滤器为`f1 f2`，则有:

* `f1` + `f2`: `f1 f2` 同时接收则接受，否则拒绝
* `f1` -`f2`： `f1` 接受同时 `f2` 拒绝则接受，否则拒绝
* `f1` | `f2`： `f1` 接受或者 `f2` 拒绝则接受，否则拒绝
* `-f1`: `f1` 拒绝则接受，否则拒绝

所有的运算符支持多个过滤器级联使用。 `self.filter` 默认为 `html_filter`，实际上 `html_filter = url_filter - static_filter` ， 即提取接受所有具有合法URL[1]且不为静态文件的请求。

`GenerationFilter` 并不对请求的 URL 进行检查，而是检查请求的深度(`Request.generation`)，每一个初始请求的深度为0，初始请求产生的请求深度为1，深度为1的请求产生的请求深度为2。`easy_spider` 爬取的方法为**广度优先**。

去重过滤器还包含了 [BloomFilter](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/filters/history_filter.py) 以及 [HashFilter](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/filters/history_filter.py) 对已完成的请求进行过滤，即 `URL` 去重的功能。`easy_spider` 默认采用 `HashFilter` 进行去重，可以将 `self.crawled_filter` [2] 修改为 `BloomFilter` 以节约内存。

1. 某些时候如  `<a href="javascript: callback">click</a>` 提取的 `URL` 为 `javascript: callback` ，不是合法的URL 。
2. 这里必须设置 `self.crawled_filter` 而不是使用 `self.filter`。这去重过滤器也无法和普通的过滤器进行运算，否则无法实现去重的功能。

### 请求对象

使用默认参数的 `Request` 对象能满足大部分的需求，但是 `Request` 也支持许多自定义的参数:

```
method: str = 请求方法 GET|POST|PUT|DELETE 
timeout: int = 超时时间
headers: dict = 请求头，默认{}
cookies: dict = cookies，默认{}
encoding: str = 编码方式，默认utf-8
params: dict = URL参数，默认{}
data: dict = 数据，取决于 data_format
data_format: str = 数据格式 FORM|JSON，若为 FORM 数据通过 application/x-www-form-urlencoded 格式传递，若为 JSON 则通过 application/json。
proxy: str = 代理，默认为空
handler: str = 处理该 Request 的回调函数
```
其中 `handler` 属性用于定义该请求完成时的回调处理函数。默认情况下，将采用 `Spider` 对象中的`handle` 方法。当然你也可以设置任何自己的方法进行处理。

### 响应对象

一个请求对象经由[AsyncClient](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/network/client.py)[1]，发起请求后将返回一个响应对象，即在 handle 方法中处理的对象。`easy_spider` 默认根据 `content_type` 生成三种不同的响应对象，如果 `content_type` 包含`text/html` 则  [HtmlResponse](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/network/response.py)，如果 `content_type` 包含除 `text/html` 以外的 `text/*` 对象，则返回[TextResponse](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/network/response.py)，否则返回[Response](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/network/response.py)。其中不同的响应对象有不同的属性，从 `Response -> TextResponse -> HtmlResponse` 逐渐增多。

`Response` 对象具有的属性:

* headers: HTTP 响应头

* body: HTTP 响应体，为未解码的 bytes 类型
* url: 响应对象的 `URL`
* request: 产生该响应对应的请求

`TextResponse` 在 `Response` 基础上增加了:

* text: 解码后的文本内容，`TextResponse` 会自动猜测 `body` 的编码类型进行解码，尽量避免乱码产生

`HtmlResponse`  在 `TextResponse` 基础上增加了:

* bs:  利用 text 属性构建的 [Beautiful Soup4](https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/) 对象

### 默认请求参数

很多时候需要定义一系列默认参数，而不是在每个请求中都声明，在 `easy_spider` 中所有定义在 `spider` 中与请求对象相同的属性都将复制给每一个新产生的请求，包括初始请求:

```python
class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["https://github.blog/"]
        self.cookies = {"key": "value"}  # 用于设置默认请求参数

    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        yield self.from_url(urls)  # 所有请求的 cookies 都将设置与 self.cookies 相同
```

### 自定义处理方法

可以通过设置请求对象的 `handler` 属性来设置处理该请求返回的响应:
```python
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse

class MySpider(AsyncSpider):

    def init(self):
        self.cookies = {"key": "value"}  # 用于设置默认请求参数
        self.start_targets = ["https://github.blog/"]

    def handle(self, response: HTMLResponse):
        urls = [response.url_join(a.attrs["href"]) for a in response.bs.select("a")]
        for url in urls:
            if url.endswith("xxx"):
                yield Request(url, handler=self.handle_other)  # 该请求返回的 response 将由 handle_other 方法处理
            else:
                yield Request(url, handler=self.handle)

    def handle_other(self, response):
        # do something
        pass

async_env.run(MySpider())
```

### 请求中间件

在 `easy_spider` 中，所有的请求都将经过请求中间件的处理。请求中间件是一系列对请求进行变换的类，其都继承于[RequestMiddleware](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/middlewares/build_in.py)，其定义如下:

``` python
class RequestMiddleware(ABC):

    @abstractmethod
    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]: pass
```

其核心方法`transform`接受一个可迭代的请求集合，以及产生这些请求的 `Response` 对象如果为初始请求，则 `Response` 对象为 `None`。`transform`根据这些参数产生新的可迭代的请求集合。

`easy_spider` 许多功能都通过中间件实现，如`过滤器`、`去重过滤器` 以及 `默认参数`。例如`ExtractorFilterMiddleware(self.filter)`  接受 `self.filter `为参数，将所有 `self.filter ` 拒绝的请求从输入的请求集合中除去。 默认采用了以下中间件:

```python
    def middlewares(self):
        return ChainMiddleware(GenerationMiddleware(),  # 设置请求为第 n 代，支持GenerationFilter 过滤器
                               ExtractorFilterMiddleware(self.filter),  # 用于支持过滤器
                               FilterMiddleware(self.crawled_filter),  # 支持去重过滤器
                               SetAttrMiddleware(self))  # 用于设置请求默认参数
```

其中 `ChainMiddleware` 用于将多个中间件合并为一个中间件进行执行[1]。用于可以编写自己的请求中间并重写`spider` 对象的`middlewares` 方法以扩展 `easy_spider` 的功能。例如某些时候需要将初始爬取目标保存在文件中，使用时读取:

```python
from typing import Iterable, Optional
from easy_spider import async_env, AsyncSpider, Request, HTMLResponse, Response
from easy_spider.middlewares.build_in import RequestMiddleware, ChainMiddleware
from easy_spider.tool import get_abs_path
from easy_spider import GenerationFilter
from os.path import join

class LoadFileMiddleware(RequestMiddleware):
    def transform(self, requests: Iterable[Request], response: Optional[Response]) -> Iterable[Request]:
        if not response:  # 如果为初始请求，则从文件中构造请求
            url = list(requests)[0].url
            with open(join(get_abs_path(__file__), url), encoding='utf-8') as fd:
                for line in fd.readlines():
                    yield Request.of(line.strip("\n"))
        else:  # 否则不做任何事情
            yield from requests

class MySpider(AsyncSpider):

    def init(self):
        self.start_targets = ["urls.txt"]

    def handle(self, response: HTMLResponse):
        titles = response.bs.select(".post-list__item a")
        print([title.text for title in titles])

    def middlewares(self):
        return ChainMiddleware(LoadFileMiddleware()).extend(super().middlewares())

async_env.run(MySpider())
```

其中，`middlewares` 中采用 `ChainMiddleware(LoadFileMiddleware()).extend(super().middlewares())`  将新的中间件以及默认的中间件结合在一起[2]，形成新的中间件并返回。

1. `ChainMiddleware` 将所有中间件按照传入的顺序进行执行
2. 如果你不是十分了解默认中间件执行的功能以及去掉它所产生的影响，建议在自定义中间件时一定要保留默认中间件，并使得自定义中间件在默认中间件前执行。

### 恢复爬虫

`easy_spider` 实现了两种可恢复的爬虫，一种是当用户主动结束爬虫，一种是被意外关闭的爬虫。对于第一种，`easy_spider` 捕获了`ctrl + c`，当你按下`ctrl + c` 时会进行一系列询问，你可以选择是否保存你的爬虫[1]。如果第二次运行该爬虫，如果检测已到保存的记录，会询问你是否继续。对于第二种，`easy_spider`提供了自动保存的功能。

你可以继承[RecoverableSpider](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/core/spider.py)来实现可恢复的爬虫。该爬虫对象与 `AsyncSpider` 使用方法相同，只是多了需要设置的参数:

* name: 爬虫的名称
* auto_save_frequence: 自动保存频率

`name` 将决定爬虫保存的路径，而 `auto_save_frequence` 将决定爬虫自动保存的频率。`auto_save_frequence = 1000` 表示每进行 `1000` 请求则保存一次爬虫。`auto_save_frequence = 0` 则不进行自动保存。

1.  爬虫保存的内存包括 `已爬取的请求` 以及 `为爬取的请求` 两大部分，其中保存的文件位置为`代码执行目录/.easy_spider/{name}` 其中 `{name}` 爬虫的属性 `self.name`。

### 请求溢出

请求溢出是指当请求达到一定数量时将请求溢出到磁盘中已节约内存，`easy_spider` 默认已经开启了此功能，可以设置 `self.num_of_spill = 0`  来关闭。同样 `self.num_of_spill ` 也指定了溢出的门限值，即若请求达到 `self.num_of_spill * 2` 则将其中的  `self.num_of_spill` 请求溢出到磁盘中。详细的溢出逻辑请参考[SpillRequestQueueProxy](https://lin3x.coding.net/p/easy_spider/d/easy_spider/git/tree/function/easy_spider/core/queue.py)。



 

