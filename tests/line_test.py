import unittest

from src.pyheatintegration.line import extract_x, y_range


class TestLine(unittest.TestCase):

    def test_y_range(self):
        self.assertEqual(
            y_range([
                ((0, 0), (1, 1)),
                ((1, 1), (2, 2)),
                ((2, 2), (3, 5)),
                ((3, 3), (5, 8))
            ]),
            (0, 8)
        )

    def test_extract_x(self):
        self.assertEqual(
            extract_x([
                ((0, 0), (1, 1)),
                ((1, 1), (2, 2)),
                ((2, 2), (3, 5)),
                ((3, 3), (5, 8))
            ]),
            [0, 1, 2, 3, 5]
        )


if __name__ == '__main__':
    unittest.main()
