import unittest
from easy_spider import tool


class A:
    def __init__(self):
        self.a = 1
        self._a = 1


class B:
    def __init__(self):
        self.a = 2


class TestTool(unittest.TestCase):

    def test_extension(self):
        ext = tool.get_extension("http://localhost:5000/%E4%B8%AD%E5%9B%BD%E7%BA%A2.txt")
        self.assertEqual(ext, "txt")

    def test_get_public_attr(self):
        a = A()
        attrs = list(tool.get_public_attr(a))
        self.assertEqual(attrs, ["a"])

    def test_copy_public_attr(self):
        a = A()
        b = A()
        tool.copy_attr("a", b, a)
        self.assertEqual(a.a, b.a)


if __name__ == '__main__':
    unittest.main()
