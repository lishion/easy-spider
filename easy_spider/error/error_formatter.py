from easy_spider.error.known_error import KnownError
from asyncio import TimeoutError
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class ExceptionFormatter:
    def __init__(self, default_formatter):
        self._default_formatter = default_formatter
        self._formatters = {}

    def register(self, exception_cls, formatter):
        self._formatters[exception_cls] = formatter

    def format(self, exception):
        formatter = self._formatters.get(exception.__type__, self._default_formatter)
        return formatter(exception)


class Formatter(ABC):

    @abstractmethod
    def _get_formatter_items(self, exception) -> Tuple[str, Optional[Exception], int]: pass

    @staticmethod
    def _no_code_exception(exception_type, detail):
        return exception_type, detail, -1

    def format(self, exception):
        exception_type, detail, code = self._get_formatter_items(exception)
        if not str(detail):
            detail = "{}.{}".format(detail.__module__, detail.__class__.__name__)
        if code == -1:
            return "{} -> {}".format(exception_type, detail)
        else:
            return "{} -> {} code: {}".format(exception_type, detail, code)


class DefaultErrorFormatter(Formatter):

    def _get_formatter_items(self, exception) -> Tuple[str, Optional[Exception], int]:
        if isinstance(exception, KnownError):
            return self._no_code_exception(exception.error_type, exception.__cause__)
        else:
            return self._no_code_exception("运行时错误", exception)


class ClientErrorFormatter(DefaultErrorFormatter):

    def _get_formatter_items(self, exception) -> Tuple[str, Optional[Exception], int]:
        if exception.__cause__.__class__ == TimeoutError:
            return self._no_code_exception(exception.error_type, "连接超时")
        else:
            return super()._get_formatter_items(exception)
