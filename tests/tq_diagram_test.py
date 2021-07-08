import unittest

from src.pyheatintegration.enums import StreamType
from src.pyheatintegration.plot_segment import PlotSegment
from src.pyheatintegration.stream import Stream
from src.pyheatintegration.tq_diagram import _create_composite_curve


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


if __name__ == '__main__':
    unittest.main()
