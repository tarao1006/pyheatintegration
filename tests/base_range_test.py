import unittest

from src.pyheatintegration.base_range import (BaseRange, flatten, get_ranges,
                                              is_continuous, merge, minmax)


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
        other = BaseRange(200.0, 300.0)

        self.assertEqual(base_range.__repr__(), "BaseRange(0.0, 100.0)")
        self.assertEqual(base_range.__str__(), "0.0->100.0")
        self.assertEqual(f"{base_range:.2f}", "0.00->100.00")

        self.assertEqual(base_range, BaseRange(0.0, 100.0))
        self.assertTrue(base_range != other)
        self.assertTrue(base_range < other)
        self.assertTrue(base_range <= other)
        self.assertTrue(other > base_range)
        self.assertTrue(other >= base_range)

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


class TestMerger(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            merge(BaseRange(0, 10), BaseRange(10, 20)),
            BaseRange(0, 20),
        )

    def test_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            merge(BaseRange(0, 10), BaseRange(5, 20))


class TestIsContinuous(unittest.TestCase):

    def test_should_return_none(self):
        self.assertIsNone(is_continuous([
            BaseRange(0, 10),
            BaseRange(10, 20),
        ]))

    def test_should_return_tuple(self):
        self.assertEqual(
            is_continuous([
                BaseRange(0, 10),
                BaseRange(5, 20),
            ]),
            (10, 5)
        )


class TestFlatten(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            flatten([
                BaseRange(0, 10),
                BaseRange(10, 20),
            ]),
            [0, 10, 20]
        )

    def test_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            flatten([
                BaseRange(0, 10),
                BaseRange(5, 20),
            ])


class TestGetRanges(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            get_ranges([0, 10, 20], BaseRange),
            [BaseRange(0, 10), BaseRange(10, 20)]
        )


if __name__ == '__main__':
    unittest.main()
