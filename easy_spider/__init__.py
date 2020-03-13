# from .context import Context
# from core.job import MultiThreadJob, AsyncJob
# from core.spider import MultiThreadSpider, AsyncSpider
# from handlers.handler import CustomHandler
# import asyncio
#
#
# class SpiderTask:
#
#     def __init__(self, context: Context):
#         self._context = context
#         self._context.init()
#
#     def handler(self, filter=None, name="default"):
#         def wrapper(func):
#             self._context.handlers.append(CustomHandler(func, filter, name))
#             return func
#         return wrapper
#
#     def run(self, num_threads=3):
#         spider = MultiThreadSpider(self._context.request, self._context.handlers, self._context.extractor)
#         MultiThreadJob(spider,
#                        self._context.resource_queue,
#                        num_threads).start()
#
#
# class AsyncSpiderTask(SpiderTask):
#
#     def __init__(self, context):
#         super().__init__(context)
#
#     async def _async_run(self, num_threads):
#         spider = AsyncSpider(self._context.request, self._context.handlers, self._context.extractor)
#         await AsyncJob(spider,
#                        self._context.resource_queue,
#                        num_threads).start()
#
#     def run(self, num_threads=3):
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(self._async_run(num_threads))
