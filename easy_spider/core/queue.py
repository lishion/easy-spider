from easy_spider.network.request import SimpleRequestQueue, SpillRequestQueueProxy, \
    RecoverableSpillRequestQueueProxy, RecoverableRequestQueue
from easy_spider.core.spider import AsyncSpider, RecoverableSpider, Spider


def get_queue_for_spider(spider):
    if not isinstance(spider, Spider):
        raise TypeError("unknown spider type `{}`".format(spider.__class__.__name__))
    num_of_spill = spider.num_of_spill
    if isinstance(spider, RecoverableSpider):
        queue = RecoverableRequestQueue()
        if num_of_spill:
            return RecoverableSpillRequestQueueProxy(queue, num_of_spill=num_of_spill)
        else:
            return queue
    if isinstance(spider, AsyncSpider):
        queue = SimpleRequestQueue()
        if num_of_spill:
            return SpillRequestQueueProxy(queue, num_of_spill=num_of_spill)
        else:
            return queue


