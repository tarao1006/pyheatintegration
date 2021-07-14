import unittest

from src.pyheatintegration.temperature_range import (
    TemperatureRange, accumulate_heats, get_temperature_ranges,
    get_temperature_transition, is_continuous)


class TestGetTemperatureRange(unittest.TestCase):

    def test_sorted(self):
        self.assertEqual(
            get_temperature_ranges([
                0.0, 10.0, 20.0
            ]),
            [
                TemperatureRange(0.0, 10.0),
                TemperatureRange(10.0, 20.0)
            ]
        )

    def test_unsorted(self):
        self.assertEqual(
            get_temperature_ranges([
                0.0, 20.0, 10.0
            ]),
            [
                TemperatureRange(0.0, 10.0),
                TemperatureRange(10.0, 20.0)
            ]
        )


class TestGetTemperatureTransition(unittest.TestCase):

    def test_get_temperature_transition(self):
        self.assertEqual(
            [0, 10, 20, 30, 30, 40, 50, 70, 70],
            sorted(get_temperature_transition([
                TemperatureRange(0, 10),
                TemperatureRange(20, 50),
                TemperatureRange(30, 30),
                TemperatureRange(40, 70),
                TemperatureRange(70, 70)
            ]))
        )


class TestIsContinuous(unittest.TestCase):

    def test_is_continuous(self):
        self.assertIsNone(is_continuous([
            TemperatureRange(0, 10),
            TemperatureRange(10, 20),
        ]))

    def test_is_continuous_erorr(self):
        self.assertEqual(
            is_continuous([
                TemperatureRange(0, 10),
                TemperatureRange(5, 20),
            ]),
            (10, 5)
        )


class TestAccumulateHeats(unittest.TestCase):

    def test_accumulate_heats(self):
        self.assertEqual(accumulate_heats([
            TemperatureRange(0, 10),
            TemperatureRange(10, 20),
            TemperatureRange(20, 30),
        ], {
            TemperatureRange(20, 30): 30.0,
            TemperatureRange(0, 10): 10.0,
            TemperatureRange(10, 20): 20.0,
        }), [
            0.0, 10.0, 30.0, 60.0
        ])

    def test_accumulate_heats_error(self):
        with self.assertRaises(ValueError):
            accumulate_heats([
                TemperatureRange(0, 10),
                TemperatureRange(10, 20)
            ], {
                TemperatureRange(0, 10): 10.0
            })


if __name__ == '__main__':
    unittest.main()
