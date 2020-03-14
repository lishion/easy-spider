import unittest
from easy_spider.tool import get_abs_path


def discover_test_suit():
    loader = unittest.TestLoader()
    abs_path = get_abs_path(__file__)
    return loader.discover(abs_path, "test_*.py")


def run_test():
    test_suit = discover_test_suit()
    runner = unittest.TextTestRunner()
    runner.run(test_suit)


if __name__ == '__main__':
    run_test()
