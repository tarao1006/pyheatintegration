import unittest

from src.pyheatintegration.enums import StreamType
from src.pyheatintegration.grand_composite_curve import GrandCompositeCurve
from src.pyheatintegration.stream import Stream


class GrandCompositeCurveTest(unittest.TestCase):

    def setUp(self):
        streams = [
            Stream(40.0, 90.0, 150.0, StreamType(1)),
            Stream(80.0, 110.0, 180.0, StreamType(1)),
            Stream(125.0, 80.0, 180.0, StreamType(2)),
            Stream(100.0, 60.0, 160.0, StreamType(2)),
        ]
        minimum_approach_temp_diff = 10.0
        self.gcc = GrandCompositeCurve(streams, minimum_approach_temp_diff)

    def test_lackgin_heats(self):
        pass

    def test_gcc(self):
        self.assertEqual(self.gcc.temps, [50.0, 60.0, 80.0, 90.0, 100.0, 120.0, 125.0])
        self.assertEqual(self.gcc.heats, [40.0, 70.0, 50.0, 0.0, 10.0, 50.0, 30.0])
        self.assertEqual(self.gcc.minimum_pinch_point_temp, 90.0)
        self.assertEqual(self.gcc.maximum_pinch_point_temp, 90.0)


if __name__ == '__main__':
    unittest.main()
