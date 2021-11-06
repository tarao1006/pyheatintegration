import unittest

from src.pyheatintegration.pinch_analyzer import PinchAnalyzer
from src.pyheatintegration.streams import Stream


class TestPinchAnalyzer(unittest.TestCase):

    def test_duplication_id(self):
        self.assertEqual(
            '流体のidは一意である必要があります。重複しているid: a',
            PinchAnalyzer.validate_streams([
                Stream(10, 20, 100, id_='a'),
                Stream(15, 25, 100, id_='a'),
            ])
        )

    def test_empty_hot_streams(self):
        self.assertEqual(
            '与熱流体および受熱流体は少なくとも1つは指定する必要があります。',
            PinchAnalyzer.validate_streams([Stream(10, 20, 100)])
        )

    def test_empty_cold_streams(self):
        self.assertEqual(
            '与熱流体および受熱流体は少なくとも1つは指定する必要があります。',
            PinchAnalyzer.validate_streams([Stream(20, 10, 100)])
        )

    def test_hot_maximum_temp_below_cold_minimum_temp(self):
        self.assertEqual(
            '与熱流体の最高温度が受熱流体の最低温度を下回っています。',
            PinchAnalyzer.validate_streams([
                Stream(40, 50, 100),
                Stream(30, 10, 100)
            ])
        )

    def test_hot_minimum_temp_below_cold_minimum_temp(self):
        self.assertEqual(
            ('与熱流体の最低温度が受熱流体の最低温度を下回っています。'
             '与熱流体最低温度: 35.000 ℃ '
             '受熱流体最低温度: 40.000 ℃'),
            PinchAnalyzer.validate_streams([
                Stream(40, 50, 100),
                Stream(50, 35, 100)
            ])
        )

    def test_hot_maximum_temp_below_cold_maximum_temp(self):
        self.assertEqual(
            ('与熱流体の最高温度が受熱流体の最高温度を下回っています。'
             '与熱流体最高温度: 45.000 ℃ '
             '受熱流体最高温度: 50.000 ℃'),
            PinchAnalyzer.validate_streams([
                Stream(40, 50, 100),
                Stream(45, 40, 100)
            ])
        )

    def test_no_error(self):
        self.assertEqual(
            '',
            PinchAnalyzer.validate_streams(
                [Stream(10, 20, 100), Stream(25, 15, 100)]
            )
        )


if __name__ == '__main__':
    unittest.main()
