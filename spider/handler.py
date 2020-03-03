from abc import abstractmethod, ABC
from spider.filter import Filter
from .response import Response, HTMLResponse


class Handler(ABC):

    def __init__(self, filter=None, name="default"):
        self.filter = filter
        self.name = name

    @abstractmethod
    def handle(self, response: Response): pass


class HTMLHandler(Handler, ABC):

    @abstractmethod
    def handle(self, response: HTMLResponse): pass


class CustomHandler(Handler):
    def __init__(self, func, filter=None, name="default"):
        super().__init__(filter, name)
        self._func = func

    def handle(self, response: Response):
        self._func(response)

