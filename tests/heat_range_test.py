import unittest

from src.pyheatintegration.heat_range import (HeatRange,
                                              get_merged_heat_ranges,
                                              get_heat_ranges, get_heats,
                                              is_continuous)


class TestHeatRange(unittest.TestCase):

    def test_merge_should_success(self):
        self.assertEqual(
            HeatRange(0, 20),
            HeatRange(0, 10).merge(HeatRange(10, 20))
        )

        self.assertEqual(
            HeatRange(0, 20),
            HeatRange(10, 20).merge(HeatRange(0, 10))
        )

    def test_merge_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            HeatRange(10, 20).merge(HeatRange(5, 40))


class TestGetHeatRanges(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            [
                HeatRange(0, 10),
                HeatRange(10, 20)
            ],
            get_heat_ranges([0, 10, 20])
        )


class TestGetHeats(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            [0, 10, 20],
            get_heats([
                HeatRange(0, 10),
                HeatRange(10, 20)
            ])
        )

    def test_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            get_heats([
                HeatRange(0, 10),
                HeatRange(20, 30)
            ])


class TestIsContinuous(unittest.TestCase):

    def test_should_return_none(self):
        self.assertIsNone(is_continuous([
            HeatRange(0, 10),
            HeatRange(10, 20),
        ]))

    def test_should_return_tuple(self):
        self.assertEqual(
            is_continuous([
                HeatRange(0, 10),
                HeatRange(5, 20),
            ]),
            (10, 5)
        )


class TestGetMergedHeatRanges(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(get_merged_heat_ranges([[
            HeatRange(0, 15),
            HeatRange(15, 30),
        ], [
            HeatRange(10, 20),
            HeatRange(20, 31),
        ]]), [
            HeatRange(0, 10),
            HeatRange(10, 15),
            HeatRange(15, 20),
            HeatRange(20, 30),
            HeatRange(30, 31),
        ])

    def test_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            get_merged_heat_ranges([[
                HeatRange(0, 15),
                HeatRange(10, 30),
            ], [
                HeatRange(10, 20),
                HeatRange(20, 40),
            ]])


if __name__ == '__main__':
    unittest.main()
