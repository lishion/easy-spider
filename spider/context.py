from .handler import Handler
from .extractor import Extractor, SimpleBSExtractor
from .request import Request, SimpleRequest, AsyncRequest
from typing import List
from .resource import ResourceQueue, SyncResourceQueue, SimpleResourceQueue
from requests import Session
from .filter import Filter
from aiohttp import ClientSession


class Context:
    def __init__(self,
                 start_resource,
                 extractor_filter: Filter,
                 extractor_type,
                 request_type,
                 session,
                 resource_queue: ResourceQueue,
                 handlers: List[Handler] = None,
                 ):
        self.handlers = handlers
        self.extractor_filter = extractor_filter
        self.extractor_type = extractor_type
        self.request_type = request_type
        self.start_resources = start_resource
        self.session = session
        self.resource_queue = resource_queue
        self.request = None
        self.extractor = None

    def init(self):
        self.resource_queue.put_many(self.start_resources)
        self.request = self.request_type(self.session)
        self.extractor = self.extractor_type(self.extractor_filter)
        self.handlers = self.handlers or []


class MultiThreadContext(Context):

    def __init__(self,
                 start_resources,
                 extractor_filter,
                 extractor_type=SimpleBSExtractor,
                 request_type=SimpleRequest,
                 handlers=None,
                 session=Session(),
                 resource_queue=SyncResourceQueue(),
                 ):
        super().__init__(start_resources,
                         extractor_filter,
                         extractor_type,
                         request_type,
                         session,
                         resource_queue,
                         handlers,
                         )
        self.session = session

    def __del__(self):
        try:
            self.session.close()
        except:
            pass


class AsyncContext(Context):

    def __init__(self,
                 start_resources,
                 extractor_filter,
                 extractor_type=SimpleBSExtractor,
                 request_type=AsyncRequest,
                 handlers=None,
                 session=ClientSession(),
                 resource_queue=SimpleResourceQueue(),
                 ):
        super().__init__(start_resources,
                         extractor_filter,
                         extractor_type,
                         request_type,
                         session,
                         resource_queue,
                         handlers,
                         )
        self.session = session

    # def __del__(self):
    #     try:
    #         self.session.close()
    #     except:
    #         pass