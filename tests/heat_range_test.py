import unittest

from src.pyheatintegration.heat_range import (HeatRange, get_heat_ranges,
                                              get_heats, is_continuous, get_detailed_heat_ranges)


class TestHeatRange(unittest.TestCase):

    def test_merge(self):
        self.assertEqual(
            HeatRange(0, 20),
            HeatRange(0, 10).merge(HeatRange(10, 20))
        )

        self.assertEqual(
            HeatRange(0, 20),
            HeatRange(10, 20).merge(HeatRange(0, 10))
        )


class TestGetHeatRanges(unittest.TestCase):

    def test_get_heat_range(self):
        self.assertEqual(
            [
                HeatRange(0, 10),
                HeatRange(10, 20)
            ],
            get_heat_ranges([0, 10, 20])
        )


class TestGetHeats(unittest.TestCase):

    def test_get_heats(self):
        self.assertEqual(
            [0, 10, 20],
            get_heats([
                HeatRange(0, 10),
                HeatRange(10, 20)
            ])
        )

    def test_get_heats_error(self):
        with self.assertRaises(ValueError):
            get_heats([
                HeatRange(0, 10),
                HeatRange(20, 30)
            ])


class TestIsContinuous(unittest.TestCase):

    def test_is_continuous(self):
        self.assertIsNone(is_continuous([
            HeatRange(0, 10),
            HeatRange(10, 20),
        ]))

    def test_is_continuous_erorr(self):
        self.assertEqual(
            is_continuous([
                HeatRange(0, 10),
                HeatRange(5, 20),
            ]),
            (10, 5)
        )


class TestGetDetailedHeatRanges(unittest.TestCase):

    def test_get_detailed_heat_ranges(self):
        self.assertEqual(get_detailed_heat_ranges([[
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

    def test_get_detailed_heat_ranges_error(self):
        with self.assertRaises(ValueError):
            get_detailed_heat_ranges([[
                HeatRange(0, 15),
                HeatRange(10, 30),
            ], [
                HeatRange(10, 20),
                HeatRange(20, 31),
            ]])


if __name__ == '__main__':
    unittest.main()
