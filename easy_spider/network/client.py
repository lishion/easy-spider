from abc import ABC, abstractmethod
from easy_spider.network.request import Request
from easy_spider.network.response import (Response, TextResponse, HTMLResponse)
from aiohttp import ClientSession, ClientTimeout


class Client(ABC):

    @abstractmethod
    def do_request(self, resource: Request) -> Response: pass

    @staticmethod
    def to_response(content, url, headers):
        content_type = headers.get("Content-Type")
        args = (content, url, headers)
        if content_type:
            if "text/html" in content_type:
                return HTMLResponse(*args)
            elif "text/" in content_type:
                return TextResponse(*args)
        return Response(*args)


class SimpleClient(Client):
    pass
    # def __init__(self, session):
    #     self._session: Session = session
    #
    # def do_request(self, resource: Request) -> Response:
    #     raw_response = self._session.get(resource.uri)
    #     return self.to_response(raw_response.content, raw_response.url, raw_response.headers)


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
            common_params["json"] = request.data_format
        else:
            raise ValueError("未知数据类型 {} ，仅支持 json 或 form")
        raw_response = await self._session.request(request.method, request.url, **common_params)
        content = await raw_response.content.read()
        return self.to_response(content, str(raw_response.url), raw_response.headers)
