from .spider import Context
from .extractor import SimpleBSExtractor
from .core import Job
from .spider import Spider
from .request import SimpleRequest
from .resource import SimpleResourceQueue
from .handler import CustomHandler


class SpiderTask:
    def __init__(self, start_urls, extractor_filter):
        self._start_urls = start_urls
        self._extractor_filter = extractor_filter
        self._handlers = []

    def handler(self, filter=None, name="default"):
        def wrapper(func):
            self._handlers.append(
                CustomHandler(func, filter, name)
            )
        return wrapper

    def run(self, num_threads=3):
        context = Context(
            self._handlers,
            SimpleBSExtractor(self._extractor_filter),
            SimpleRequest()
        )
        Job(self._start_urls, Spider(context), SimpleResourceQueue(), num_threads).start()
