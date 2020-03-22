from easy_spider.error.known_error import KnownError
from asyncio import TimeoutError
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class ErrorFormatter:
    def __init__(self, default_formatter):
        self._default_formatter = default_formatter
        self._formatters = {}

    def register(self, exception_cls, formatter):
        self._formatters[exception_cls] = formatter

    def format(self, exception):
        formatter = self._formatters.get(exception.__class__, self._default_formatter)
        return formatter.format(exception)


class Formatter(ABC):

    @abstractmethod
    def _get_formatter_items(self, exception) -> Tuple[str, Optional[Exception]]: pass

    def format(self, exception):
        exception_type, cause = self._get_formatter_items(exception)
        if not str(cause):  # 如果 cause 为空，则将异常类的名字作为 cause
            cause = "{}.{}".format(cause.__module__, cause.__class__.__name__)
        if not hasattr(exception, "code"):
            return "{} -> {}".format(exception_type, cause)
        else:
            return "{} -> {} code: {}".format(exception_type, cause, exception.code)


class DefaultErrorFormatter(Formatter):

    def _get_formatter_items(self, exception) -> Tuple[str, Optional[Exception]]:
        if isinstance(exception, KnownError):
            return exception.error_type, exception.__cause__
        else:
            return "运行时错误", exception


class ClientErrorFormatter(DefaultErrorFormatter):

    def _get_formatter_items(self, exception) -> Tuple[str, Optional[Exception]]:
        if exception.__cause__.__class__ == TimeoutError:
            return exception.error_type, Exception("连接超时")
        else:
            return super()._get_formatter_items(exception)
