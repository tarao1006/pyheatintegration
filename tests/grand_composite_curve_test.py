import unittest
from collections import defaultdict

from src.pyheatintegration.grand_composite_curve import GrandCompositeCurve, _get_lacking_heats, _get_heats
from src.pyheatintegration.stream import Stream, get_temperature_range_streams
from src.pyheatintegration.temperature_range import TemperatureRange


class GrandCompositeCurveTest(unittest.TestCase):

    def test_gcc(self):
        streams = [
            Stream(40.0, 90.0, 150.0),
            Stream(80.0, 110.0, 180.0),
            Stream(125.0, 80.0, 180.0),
            Stream(100.0, 60.0, 160.0),
        ]
        minimum_approach_temp_diff = 10.0
        self.gcc = GrandCompositeCurve(streams, minimum_approach_temp_diff)

        self.assertEqual(self.gcc.temps, [50.0, 60.0, 80.0, 90.0, 100.0, 120.0, 125.0])
        self.assertEqual(self.gcc.heats, [40.0, 70.0, 50.0, 0.0, 10.0, 50.0, 30.0])
        self.assertEqual(self.gcc.pinch_points, [(3, 90.0)])


class TestGetLackingHeats(unittest.TestCase):

    def test_should_success(self):
        streams = [
            Stream(50.0, 100.0, 150.0),
            Stream(90.0, 120.0, 180.0),
            Stream(125.0, 80.0, 180.0),
            Stream(100.0, 60.0, 160.0),
        ]

        _, temp_range_streams = get_temperature_range_streams(
            streams
        )

        self.assertEqual(
            _get_lacking_heats(temp_range_streams),
            defaultdict(int, {
                TemperatureRange(50, 60): -30,
                TemperatureRange(60, 80): 20,
                TemperatureRange(80, 90): 50,
                TemperatureRange(90, 100): -10,
                TemperatureRange(100, 120): -40,
                TemperatureRange(120, 125): 20,
            })
        )


class TestGetHeats(unittest.TestCase):

    def test_should_success(self):
        streams = [
            Stream(50.0, 100.0, 150.0),
            Stream(90.0, 120.0, 180.0),
            Stream(125.0, 80.0, 180.0),
            Stream(100.0, 60.0, 160.0),
        ]

        temp_range, temp_range_streams = get_temperature_range_streams(
            streams
        )

        self.assertEqual(
            [40, 70, 50, 0, 10, 50, 30],
            _get_heats(temp_range, temp_range_streams)
        )


if __name__ == '__main__':
    unittest.main()
