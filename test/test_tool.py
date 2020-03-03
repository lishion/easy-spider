import unittest
from spider import tool


class TestTool(unittest.TestCase):

    def test_extension(self):
        ext = tool.get_extension("http://localhost:5000/%E4%B8%AD%E5%9B%BD%E7%BA%A2.txt")
        self.assertEqual(ext, ".txt")


if __name__ == '__main__':
    unittest.main()
