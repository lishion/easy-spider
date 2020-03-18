from abc import abstractmethod, ABC
from typing import Generator
from easy_spider.network.response import HTMLResponse


class Extractor(ABC):

    @abstractmethod
    def extract(self, response) -> Generator[str, None, None]: pass


class SimpleBSExtractor(Extractor):

    def extract(self, response: HTMLResponse) -> Generator[str, None, None]:
        for tag_a in response.bs.find_all("a"):
            href = tag_a.get("href")
            if href:
                yield response.url_join(href)

