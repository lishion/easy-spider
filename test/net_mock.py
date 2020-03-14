from unittest import TestCase
from aioresponses import aioresponses
from asyncio import get_event_loop, ensure_future
from aiohttp import ClientSession
from easy_spider.network.client import AsyncClient


class NetMockTestCase(TestCase):
    mocked = aioresponses()
    mocked.start()
    loop = get_event_loop()
    session = None
    client = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.session = None
        cls.client = None

    @classmethod
    def prepare(cls):
        if cls.session is None:
            cls.session = ClientSession()
        if cls.client is None:
            cls.client = AsyncClient(cls.session)

    @classmethod
    def run_and_get_result(cls, cor):
        future = ensure_future(cor)
        cls.loop.run_until_complete(future)
        return future.result()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mocked.stop()
        if cls.session:
            cls.run_and_get_result(cls.session.close())
        cls.loop.close()
