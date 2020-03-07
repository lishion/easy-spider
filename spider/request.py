from abc import ABC, abstractmethod
from spider.resource import Resource
from spider.response import (Response, TextResponse, HTMLResponse)
from requests import Session
import requests
from aiohttp import ClientSession


class Request(ABC):

    @abstractmethod
    def do_request(self, resource: Resource) -> Response: pass


class SimpleRequest(Request):
    def __init__(self, session=None):
        self._session: Session = session or Session()

    @staticmethod
    def to_response(content, url, headers):
        content_type = headers.get("Content-Type")
        args = (content, url, headers)
        if content_type:
            if "text/plain" in content_type:
                return TextResponse(*args)
            elif "text/html" in content_type:
                return HTMLResponse(*args)
        return Response(*args)

    def do_request(self, resource: Resource) -> Response:
        raw_response = self._session.get(resource.uri)
        return self.to_response(raw_response.content, raw_response.url, raw_response.headers)

    def __del__(self):
        self._session.close()


class AsyncRequest(SimpleRequest):

    def __init__(self, session):
        super().__init__()
        self._session: ClientSession = session

    async def do_request(self, resource: Resource):
        raw_response = await self._session.get(resource.uri)
        content = await raw_response.content.read()
        return self.to_response(content, raw_response.url, raw_response.headers)

    def __del__(self): pass
