import unittest

from src.pyheatintegration.heat_range import HeatRange


class TestHeatRnage(unittest.TestCase):

    def test_heat_range(self):
        self.assertEqual(
            HeatRange(0, 10).__repr__(),
            "HeatRange(0, 10)"
        )


if __name__ == '__main__':
    unittest.main()
