import unittest

from src.pyheatintegration.heat_range import HeatRange
from src.pyheatintegration.plot_segment import (PlotSegment, get_plot_segments,
                                                temp_diff)


class TestPlotSegmtn(unittest.TestCase):

    def test_plot_segment(self):
        plot_segment = PlotSegment(0.0, 100.0, 100.0, 300.0)

        self.assertEqual(
            plot_segment.__str__(),
            "heat: (0.0; 100.0) temperature: (100.0; 300.0)"
        )

        self.assertEqual(
            plot_segment.__repr__(),
            "PlotSegment(0.0, 100.0, 100.0, 300.0)"
        )

        self.assertEqual(
            plot_segment.__format__(".2f"),
            "PlotSegment(0.00, 100.00, 100.0, 300.0)"
        )

        self.assertEqual(plot_segment.line(), ((0, 100), (100, 300)))
        self.assertEqual(plot_segment.heats(), (0, 100))
        self.assertEqual(plot_segment.start_heat(), 0)
        self.assertEqual(plot_segment.finish_heat(), 100)
        self.assertEqual(plot_segment.temperatures(), (100, 300))
        self.assertEqual(plot_segment.start_temperature(), 100)
        self.assertEqual(plot_segment.finish_temperature(), 300)
        self.assertTrue(plot_segment.contain_heat(50))
        self.assertFalse(plot_segment.contain_heat(200))
        self.assertTrue(plot_segment.contain_heats([50, 70]))
        self.assertTrue(plot_segment.contain_temperature(150))
        self.assertTrue(plot_segment.temperature_at_heat(10), 120)
        self.assertTrue(plot_segment.temperatures_at_heats((10, 20)), (120, 140))

        with self.assertRaises(ValueError):
            plot_segment.heat_at_temperature(800)

    def test_merge(self):
        plot_segment = PlotSegment(0.0, 100.0, 100.0, 300.0, 1)
        other_mergiable = PlotSegment(100, 200, 300, 500, 1)
        other_not_mergiable = PlotSegment(100, 200, 300, 500, 2)

        self.assertTrue(plot_segment.mergiable(other_mergiable))
        self.assertFalse(plot_segment.mergiable(other_not_mergiable))

        self.assertEqual(
            plot_segment.merge(other_mergiable),
            PlotSegment(0, 200, 100, 500, 1)
        )


class TestTempDiff(unittest.TestCase):

    def test_temp_diff(self):
        self.assertEqual(
            temp_diff(
                PlotSegment(0, 100, 200, 300),
                PlotSegment(0, 100, 50, 100),
            ),
            (150, 200)
        )


class TestGetPlotSegments(unittest.TestCase):

    def test_get_plot_segments(self):
        self.assertEqual(get_plot_segments(
            [
                HeatRange(0, 10),
                HeatRange(10, 20),
                HeatRange(20, 50)
            ],
            [
                PlotSegment(0, 20, 100, 200),
                PlotSegment(20, 50, 200, 300)
            ]
        ), [
            PlotSegment(0, 10, 100, 150),
            PlotSegment(10, 20, 150, 200),
            PlotSegment(20, 50, 200, 300)
        ])


if __name__ == '__main__':
    unittest.main()
