import unittest
from collections import defaultdict

from src.pyheatintegration.enums import StreamType
from src.pyheatintegration.errors import InvalidStreamError
from src.pyheatintegration.stream import Stream, get_temperature_range_streams, is_valid_streams
from src.pyheatintegration.temperature_range import TemperatureRange


class TestStream(unittest.TestCase):

    def test_zero_heat_flow(self):
        with self.assertRaises(InvalidStreamError):
            Stream(0.0, 10.0, 0.0, StreamType(1))
            Stream(0.0, 10.0, 0.0, StreamType(2))

    def test_nonzero_heat_flow(self):
        with self.assertRaises(InvalidStreamError):
            Stream(0.0, 10.0, 10.0, StreamType(3))
            Stream(0.0, 10.0, 10.0, StreamType(4))

    def test_low_output_temperature(self):
        with self.assertRaises(InvalidStreamError):
            Stream(10.0, 0.0, 10.0, StreamType(1))
            Stream(10.0, 0.0, 0.0, StreamType(3))

    def test_low_input_temperature(self):
        with self.assertRaises(InvalidStreamError):
            Stream(0.0, 10.0, 10.0, StreamType(2))
            Stream(0.0, 10.0, 0.0, StreamType(4))


class TestGetTemperatureRangeStreams(unittest.TestCase):

    def test_get_temperature_range_streams(self):
        streams = [
            Stream(0.0, 10.0, 10.0, StreamType(1)),
            Stream(20.0, 50.0, 30.0, StreamType(1)),
            Stream(50.0, 50.0, 10.0, StreamType(1)),
            Stream(80.0, 100.0, 20.0, StreamType(1)),
            Stream(90.0, 90.0, 10.0, StreamType(1)),
        ]

        expected = defaultdict(set)
        expected[TemperatureRange(0.0, 10.0)] = {Stream(0.0, 10.0, 10.0, StreamType(1))}
        expected[TemperatureRange(10.0, 20.0)] = set()
        expected[TemperatureRange(20.0, 50.0)] = {Stream(20.0, 50.0, 30.0, StreamType(1))}
        expected[TemperatureRange(50.0, 50.0)] = {Stream(50.0, 50.0, 10.0, StreamType(1))}
        expected[TemperatureRange(50.0, 80.0)] = set()
        expected[TemperatureRange(80.0, 90.0)] = {Stream(80.0, 90.0, 10.0, StreamType(1))}
        expected[TemperatureRange(90.0, 90.0)] = {Stream(90.0, 90.0, 10.0, StreamType(1))}
        expected[TemperatureRange(90.0, 100.0)] = {Stream(90.0, 100.0, 10.0, StreamType(1))}

        temp_ranges, result = get_temperature_range_streams(streams)

        for temp_range in temp_ranges:
            result_streams: list[Stream] = sorted(list(result[temp_range]), key=lambda s: s.input_temperature())
            expected_streams: list[Stream] = sorted(list(expected[temp_range]), key=lambda s: s.input_temperature())

            self.assertEqual(len(result_streams), len(expected_streams))
            for i in range(len(result_streams)):
                result_stream = result_streams[i]
                expected_stream = expected_streams[i]

                self.assertEqual(result_stream.temperature_range, expected_stream.temperature_range)
                self.assertEqual(result_stream.heat_flow, expected_stream.heat_flow)
                self.assertEqual(result_stream.type_, expected_stream.type_)


class TestIsValidStreams(unittest.TestCase):

    def test_is_valid_streams(self):
        self.assertTrue(is_valid_streams([
            Stream(40, 90, 150),
            Stream(80, 110, 180),
            Stream(125, 80, 160),
            Stream(100, 60, 160)
        ]))

        self.assertFalse(is_valid_streams([
            Stream(40, 90, 150),
            Stream(80, 110, 180)
        ]))


if __name__ == '__main__':
    unittest.main()
