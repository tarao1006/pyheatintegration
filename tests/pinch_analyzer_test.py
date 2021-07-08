import unittest

from src.pyheatintegration.pinch_analyzer import PinchAnalyzer


class TestPinchAnalyzer(unittest.TestCase):

    def test(self):
        with self.assertRaises(RuntimeError):
            PinchAnalyzer([], 10.0)


if __name__ == '__main__':
    unittest.main()
