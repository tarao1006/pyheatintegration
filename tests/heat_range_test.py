import unittest

from src.pyheatintegration.heat_range import HeatRange, get_merged_heat_ranges


class TestHeatRnage(unittest.TestCase):

    def test_heat_range(self):
        self.assertEqual(
            HeatRange(0, 10).__repr__(),
            "HeatRange(0, 10)"
        )


class TestGetMergedHeatRanges(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            get_merged_heat_ranges([
                [HeatRange(0, 10), HeatRange(10, 30)],
                [HeatRange(5, 15), HeatRange(15, 40)]
            ]),
            [HeatRange(0, 5), HeatRange(5, 10), HeatRange(10, 15), HeatRange(15, 30), HeatRange(30, 40)]
        )

    def test_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            get_merged_heat_ranges([
                [HeatRange(0, 10), HeatRange(5, 30)],
                [HeatRange(5, 15), HeatRange(15, 40)]
            ])


if __name__ == '__main__':
    unittest.main()
