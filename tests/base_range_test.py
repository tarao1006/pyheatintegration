import unittest

from src.pyheatintegration.base_range import BaseRange, minmax


class TestMinMax(unittest.TestCase):

    def test_different_value(self):
        self.assertEqual(minmax(20, 10), (10, 20))
        self.assertEqual(minmax(10, 20), (10, 20))
        self.assertEqual(minmax(-10, 20), (-10, 20))
        self.assertEqual(minmax(-10, -20), (-20, -10))

    def test_same_value(self):
        self.assertEqual(minmax(10, 10), (10, 10))
        self.assertEqual(minmax(-10, -10), (-10, -10))


class TestBaseRange(unittest.TestCase):

    def test_base_range(self):
        base_range = BaseRange(0.0, 100.0)

        self.assertEqual(base_range.__repr__(), "BaseRange(0.0, 100.0)")
        self.assertEqual(base_range.__str__(), "0.0->100.0")

        self.assertEqual(base_range.delta, 100)
        self.assertEqual(base_range.start, 0)
        self.assertEqual(base_range.finish, 100)
        self.assertTrue(base_range(), (0.0, 100.0))
        self.assertTrue(10.0 in base_range)
        self.assertFalse(200.0 in base_range)
        self.assertTrue(base_range.mergeable(BaseRange(100, 200)))
        self.assertFalse(base_range.mergeable(BaseRange(200, 300)))

        base_range.shift(10.0)
        self.assertTrue(base_range(), (10.0, 110.0))
        self.assertEqual(base_range.start, 10.0)
        self.assertEqual(base_range.finish, 110.0)


if __name__ == '__main__':
    unittest.main()
