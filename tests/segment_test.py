import unittest

from src.pyheatintegration.heat_range import HeatRange
from src.pyheatintegration.segment import Segment
from src.pyheatintegration.stream import Stream
from src.pyheatintegration.enums import StreamType
from src.pyheatintegration.plot_segment import PlotSegment


class TeseSegment(unittest.TestCase):

    def test_segment(self):
        segment = Segment(
            (0, 100),
            (300, 400),
            (100, 200),
            [
                Stream(400, 300, 70, StreamType(2)),
                Stream(400, 300, 30, StreamType(2)),
            ],
            [
                Stream(100, 200, 90, StreamType(1)),
                Stream(100, 200, 10, StreamType(1)),
            ]
        )

        self.assertEqual(
            segment.hot_plot_segments_separated_streams,
            [
                PlotSegment(0, 70, 300, 400),
                PlotSegment(70, 100, 300, 400)
            ]
        )

        self.assertEqual(
            segment.cold_plot_segments_separated_streams,
            [
                PlotSegment(0, 90, 100, 200),
                PlotSegment(90, 100, 100, 200)
            ]
        )

        self.assertEqual(
            segment.heat_ranges,
            [HeatRange(0, 70), HeatRange(70, 90), HeatRange(90, 100)]
        )

        self.assertEqual(
            segment.hot_plot_segments_separated,
            [
                PlotSegment(0, 70, 300, 400),
                PlotSegment(70, 90, 300, 300 + 100 * 2 / 3),
                PlotSegment(90, 100, 300 + 100 * 2 / 3, 400),
            ]
        )

        self.assertEqual(
            segment.cold_plot_segments_separated,
            [
                PlotSegment(0, 70, 100, 100 + 100 * 7 / 9),
                PlotSegment(70, 90, 100 + 100 * 7 / 9, 200),
                PlotSegment(90, 100, 100, 200)
            ]
        )

    def test_split(self):
        segment = Segment(
            (0, 100),
            (300, 400),
            (100, 200),
            [
                Stream(400, 300, 70, StreamType(2)),
                Stream(400, 300, 30, StreamType(2)),
            ],
            [
                Stream(100, 200, 90, StreamType(1)),
                Stream(100, 200, 10, StreamType(1)),
            ]
        )

        segment.split(200)

        self.assertEqual(
            segment.hot_plot_segments_splitted,
            [
                PlotSegment(0, 70, 300, 400),
                PlotSegment(70, 90, 300, 400),
                PlotSegment(90, 100, 300, 400)
            ]
        )

        self.assertEqual(
            segment.cold_plot_segments_splitted,
            [
                PlotSegment(0, 70, 100, 200),
                PlotSegment(70, 90, 100, 200),
                PlotSegment(90, 100, 100, 200)
            ]
        )


if __name__ == '__main__':
    unittest.main()
