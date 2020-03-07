from spider.extractor import Extractor
from spider.handler import Handler
from spider.resource import Resource, ResourceQueue
from spider.request import Request
from typing import List
from spider.log import logger


class Context:
    def __init__(self,
                 handlers: List[Handler],
                 extractor: Extractor,
                 request: Request):
        self.handlers = handlers
        self.extractor = extractor
        self.request = request


class Spider:

    def __init__(self, context: Context):
        self._context = context

    def handle_and_extract(self, resource, response):
        for handler in self._context.handlers:  # 寻找可以处理该资源的 handler
            # 未设置 filter 表示接收所有类型的 response
            can_handle = (handler.filter is None) or handler.filter.accept(resource)
            if can_handle:
                handler.handle(response)
                logger.info(f"{resource}处理完成, handler={handler.name}")
        return self._context.extractor.extract(response)  # 从 response 提取新资源

    def crawl(self, resource: Resource):
        response = self._context.request.do_request(resource)  # 发送请求
        return self.handle_and_extract(resource, response)


class AsyncSpider(Spider):

    def __init__(self, context):
        super().__init__(context)
        self._context = context

    async def crawl(self, resource: Resource):
        response = await self._context.request.do_request(resource)
        return self.handle_and_extract(resource, response)
