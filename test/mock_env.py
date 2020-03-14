from unittest import TestCase
from aioresponses import aioresponses
from asyncio import get_event_loop, ensure_future
from aiohttp import ClientSession
from easy_spider.network.client import AsyncClient
from easy_spider.network.request import Request
from test.tools import test_page


class _MockEnv:
    def __init__(self):
        self.loop = None
        self.session = None
        self.client = None
        self.created = False
        self.mocked = aioresponses()

    async def _create_client_session(self):
        self.session = ClientSession()

    def create(self):
        if not self.created:
            self.loop = get_event_loop()
            self.loop.run_until_complete(self._create_client_session())
            self.client = AsyncClient(self.session)
            self.mocked.start()
            self.created = True

    def destroy(self):
        if self.created:
            self.loop.run_until_complete(self.session.close())
            self.mocked.stop()
            self.loop.close()

    def __del__(self):
        self.destroy()


env = _MockEnv()
env.create()
env.mocked.get("http://localhost:5000/test_extract", body=test_page, content_type="text/html", repeat=True)


async def _fetch(url):
    return await env.client.do_request(Request(url))


def get(url):
    return run_and_get_result(_fetch(url))


def run_and_get_result(cor):
    future = ensure_future(cor)
    env.loop.run_until_complete(future)
    return future.result()
