import unittest
from easy_spider.core.task import RecoverableTask, AsyncTask, CountDownRecoverableTask
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

    def test_auto_save(self):
        test_data = {"key": 1}
        spider = MySpider()
        spider.set_session(mock_env.env.session)
        spider.start_targets = ["http://localhost:5000/test_extract"]
        spider.auto_save_frequency = 10
        task = CountDownRecoverableTask(spider)
        task.add_actions(lambda: test_data.clear())
        for _ in range(5):
            mock_env.env.loop.run_until_complete(task.run())
            task._request_queue.put(Request.of("http://localhost:5000/test_extract"))
        self.assertEqual(test_data, {"key": 1})
        for _ in range(5):
            mock_env.env.loop.run_until_complete(task.run())
            task._request_queue.put(Request.of("http://localhost:5000/test_extract"))
        self.assertEqual(test_data, {})


if __name__ == '__main__':
    unittest.main()
