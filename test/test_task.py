import unittest
from easy_spider.core.task import RecoverableTask, AsyncTask
from easy_spider.core.spider import AsyncSpider, RecoverableSpider
from easy_spider.network.request import Request
from os import makedirs
from os.path import exists
from test import mock_env


class MySpider(RecoverableSpider):
    def __init__(self):
        super().__init__()
        self.start_targets = ["http://www.test.com"]
        self.name = "test_spider"

    def handle(self, response):
        pass


class TestTask(unittest.TestCase):
    def test_stash(self):
        spider = MySpider()
        spider.start_targets = ["http://localhost:5000/test_extract"]
        task = RecoverableTask(spider)
        exists(".task_stash") or makedirs(".task_stash")
        task.stash(".task_stash")
        del task
        recovered_task = RecoverableTask(MySpider())
        self.assertTrue(recovered_task.can_recover(".task_stash"))
        recovered_task.recover(".task_stash")
        self.assertTrue(recovered_task.spider.crawled_filter.contains(Request.of("http://localhost:5000/test_extract")))


if __name__ == '__main__':
    unittest.main()
