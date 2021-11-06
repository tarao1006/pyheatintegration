import unittest

from src.pyheatintegration.enums import StreamType
from src.pyheatintegration.plot_segment import PlotSegment
from src.pyheatintegration.streams import Stream
from src.pyheatintegration.tq_diagram import (
    _create_composite_curve, get_possible_minimum_temp_diff_range)


class TestCreateCompositeCurve(unittest.TestCase):

    def test_create_composite_curve(self):
        self.assertEqual(_create_composite_curve([
            Stream(0, 20, 100, StreamType(1), 0),
            Stream(10, 30, 100, StreamType(1), 0),
        ]), [
            PlotSegment(0, 50, 0, 10),
            PlotSegment(50, 150, 10, 20),
            PlotSegment(150, 200, 20, 30),
        ])

    def test_create_composite_curve_straight_line(self):
        self.assertEqual(_create_composite_curve([
            Stream(0, 20, 100, StreamType(1), 0),
            Stream(10, 30, 100, StreamType(1), 0),
            Stream(40, 40, 20, StreamType(1), 0),
        ]), [
            PlotSegment(0, 50, 0, 10),
            PlotSegment(50, 150, 10, 20),
            PlotSegment(150, 200, 20, 30),
            PlotSegment(200, 200, 30, 40),
            PlotSegment(200, 220, 40, 40),
        ])

        self.assertEqual(_create_composite_curve([
            Stream(0, 20, 100, StreamType(1), 0),
            Stream(10, 30, 100, StreamType(1), 0),
            Stream(15, 15, 20, StreamType(1), 0),
        ]), [
            PlotSegment(0, 50, 0, 10),
            PlotSegment(50, 100, 10, 15),
            PlotSegment(100, 120, 15, 15),
            PlotSegment(120, 170, 15, 20),
            PlotSegment(170, 220, 20, 30)
        ])


class TestGetPossibleMinimumTempDiffRange(unittest.TestCase):

    def test_get_possible_minimum_temp_diff_range(self):
        temp_range = get_possible_minimum_temp_diff_range([
            Stream(40.0, 90.0, 150.0, StreamType(1)),
            Stream(80.0, 110.0, 180.0, StreamType(1)),
            Stream(125.0, 80.0, 160.0, StreamType(2)),
            Stream(100.0, 60.0, 160.0, StreamType(2)),
        ])
        self.assertEqual(temp_range.finish, 15.0)


if __name__ == '__main__':
    unittest.main()
