from abc import ABC, abstractmethod
from easy_spider.network.request import Request
from easy_spider.network.response import (Response, TextResponse, HTMLResponse)
from easy_spider.error.error_handler import client_error
from easy_spider.error.known_error import ResponseError
from aiohttp import ClientSession, ClientTimeout


class Client(ABC):

    @abstractmethod
    def do_request(self, resource: Request) -> Response: pass

    @staticmethod
    def to_response(request, content, url, headers):
        content_type = headers.get("Content-Type")
        args = (content, url, headers)
        response = None
        if content_type:
            if "text/html" in content_type:
                response = HTMLResponse(*args)
            elif "text/" in content_type:
                response = TextResponse(*args)
        else:
            response = Response(*args)
        response.request = request
        return response


class AsyncClient(Client):

    def __init__(self, session=None):
        self._session: ClientSession = session

    def set_session(self, session):
        self._session = session

    async def do_request(self, request: Request):
        assert request
        common_params = dict(
            headers=request.headers,
            cookies=request.cookies,
            timeout=ClientTimeout(request.timeout),
            params=request.params
        )
        data_format = request.data_format.lower()
        if data_format == "form":
            common_params["data"] = request.data
        elif data_format == "json":
            common_params["json"] = request.data
        else:
            raise ValueError("未知数据类型 {} ，仅支持 json 或 form")
        try:
            raw_response = await self._session.request(request.method, request.url, **common_params)
            content = await raw_response.content.read()
        except Exception as e:
            raise client_error(e) from e
        if raw_response.status >= 400:
            raise ResponseError(raw_response.status) from None
        return self.to_response(request, content, str(raw_response.url), raw_response.headers)
