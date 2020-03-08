import unittest
from spider.resource import Resource


class TestResource(unittest.TestCase):
    def test_resource(self):
        r = Resource.get_from("test")
        self.assertEqual(r.uri, "test")
        self.assertEqual(r.key, "test")
        r = Resource.get_from("test", "test1", 0, "any")
        self.assertEqual(r.uri, "test")
        self.assertEqual(r.key, "test1")
        self.assertEqual(r.priority, 0)
        self.assertEqual(r.tag, "any")
        with self.assertRaises(ValueError):
            Resource.get_from()
        with self.assertRaises(ValueError):
            Resource.get_from(*([0] * 5))
        r = Resource.of(('test',), ('test', 'test', 0, 'my_tag'))
        self.assertEqual(r[0].uri, 'test')
        self.assertEqual(r[0].key, 'test')
        self.assertEqual(r[1].tag, 'my_tag')
        with self.assertRaises(ValueError):
            r = Resource.of(('1', '2', '3', '4', '5'))

if __name__ == '__main__':
    unittest.main()
