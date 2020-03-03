from .handler import CustomHandler, Handler
from .filter import Filter


def handler(filter: Filter = None, name: str = "default"):
    def wrapper(func) -> Handler:
        return CustomHandler(func, filter, name)
    return wrapper
