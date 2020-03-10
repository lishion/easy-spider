from abc import abstractmethod, ABC
from spider.resource import Resource
from typing import Generator
from .response import TextResponse, HTMLResponse
from .filter import Filter


class Extractor(ABC):

    def __init__(self, filter: Filter):
        self._filter = filter

    @property
    def filter(self): return self._filter

    @filter.setter
    def filter(self, filter):
        self._filter = filter

    @abstractmethod
    def url_to_resource(self, url: str) -> Resource: pass

    def extract(self, response) -> Generator[Resource, None, None]:
        for url in self.extract_url(response):
            resource = self.url_to_resource(url)
            if self.filter.accept(resource):
                yield resource

    @abstractmethod
    def extract_url(self, response: TextResponse) -> Generator[str, None, None]: pass


class SimpleExtractor(Extractor, ABC):

    def url_to_resource(self, url) -> Resource:
        return Resource(url, url)


class SimpleBSExtractor(SimpleExtractor):

    def extract_url(self, response: HTMLResponse) -> Generator[str, None, None]:
        for tag_a in response.bs.find_all("a"):
            if tag_a["href"]:
                yield response.url_join(tag_a["href"])

