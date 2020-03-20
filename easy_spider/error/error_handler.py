from aiohttp.client_exceptions import ClientConnectionError, ClientResponseError
from asyncio import TimeoutError
from easy_spider.error import known_error
from functools import wraps


def client_error(exception):
    if isinstance(exception, TimeoutError) or isinstance(exception, ClientConnectionError):
        return known_error.ConnectionError()
    elif isinstance(exception, ClientResponseError):
        return known_error.ResponseError(exception.status)
    else:
        return known_error.ClientError()


def handler_error(_):
    return known_error.HandlerError()


def forward(to):
    def inner(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                res = method(*args, **kwargs)
            except Exception as e:
                new_exception = to(e)
                raise new_exception from e
            return res
        return wrapper
    return inner
