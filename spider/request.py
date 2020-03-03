from abc import ABC, abstractmethod
from spider.resource import Resource
from spider.response import (Response, TextResponse, HTMLResponse)
from requests import Session
import requests


class Request(ABC):

    @abstractmethod
    def do_request(self, resource: Resource) -> Response: pass


class SimpleRequest(Request):
    def __init__(self):
        self._session: Session = Session()

    @staticmethod
    def to_response(raw_response: requests.Response):
        content_type = raw_response.headers.get("Content-Type")
        args = (raw_response.content, raw_response.url, raw_response.headers)
        if content_type:
            if "text/plain" in content_type:
                return TextResponse(*args)
            elif "text/html" in content_type:
                return HTMLResponse(*args)
        else:
            return Response(*args)

    def do_request(self, resource: Resource) -> Response:
        raw_response = self._session.get(resource.uri)
        return self.to_response(raw_response)

    def __del__(self):
        self._session.close()
