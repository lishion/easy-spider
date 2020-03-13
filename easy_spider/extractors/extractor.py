from abc import abstractmethod, ABC
from typing import Generator
from network.response import HTMLResponse


class Extractor(ABC):

    @abstractmethod
    def extract(self, response) -> Generator[str, None, None]: pass


class SimpleBSExtractor(Extractor):

    def extract(self, response: HTMLResponse) -> Generator[str, None, None]:
        for tag_a in response.bs.find_all("a"):
            if tag_a["href"]:
                yield response.url_join(tag_a["href"])

