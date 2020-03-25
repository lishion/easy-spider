from abc import ABC, abstractmethod
from collections import deque
from easy_spider.core.recoverable import FileBasedRecoverable
from easy_spider.tool import EXE_PATH, uuid, pickle_load, pickle_dump, formatted_datetime, delete_file
from os.path import join, exists
from os import makedirs
from easy_spider.log import console_logger
from typing import List


class Request(ABC):
    def __init__(self, url, handler=None, method='GET', priority=0, tag="any",
                 headers=None, cookies=None, timeout=None, params=None, data=None,
                 data_format='form', encoding='utf-8', generation=0):
        self.url: str = url
        self._handler = handler
        self.priority: int = priority
        self.tag = tag
        self.method: str = method
        self.timeout: int = timeout
        self.headers: dict = headers or {}
        self.cookies: dict = cookies or {}
        self.encoding: str = encoding
        self.params: dict = params or {}
        self.data: dict = data
        self.data_format: str = data_format
        self.generation = generation

    @property
    def handler(self):
        return self._handler

    @handler.setter
    def handler(self, callback):
        if not callable(callback):
            raise TypeError("handler must be a callable, but get type: `{}`".format(type(callback).__name__))
        self._handler = callback

    def __repr__(self):
        return "[method={} uri={}]".format(self.method, self.url)

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def of(instance):
        if isinstance(instance, Request):
            return instance
        elif isinstance(instance, str):
            return Request(instance)
        else:
            raise TypeError("can't build request from type `{}`".format(type(instance).__name__))
