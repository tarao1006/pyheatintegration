import unittest

from src.pyheatintegration.line import convert_to_excel_data, extract_x, y_range


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


class TestConvertToExcelData(unittest.TestCase):

    def test_should_success(self):
        self.assertEqual(
            ([0, 1, 3, 4], [0, 2, 3, 5]),
            convert_to_excel_data([((0, 0), (1, 2)), ((1, 2), (3, 3)), ((3, 3), (4, 5))])
        )
        self.assertEqual(
            ([0, 1, 1, 2], [0, 2, 0, 2]),
            convert_to_excel_data([((0, 0), (1, 2)), ((1, 0), (2, 2))])
        )


if __name__ == '__main__':
    unittest.main()
