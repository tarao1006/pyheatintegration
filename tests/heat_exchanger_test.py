import unittest

from src.pyheatintegration.enums import StreamState
from src.pyheatintegration.heat_exchanger import get_overall_heat_transfer_coefficient


class TestGetOverallHeatTransferCoefficient(unittest.TestCase):

    def test_success(self):
        self.assertEqual(
            get_overall_heat_transfer_coefficient(
                StreamState.LIQUID, StreamState.LIQUID
            ),
            300.0
        )

    def test_failure(self):
        with self.assertRaises(ValueError):
            get_overall_heat_transfer_coefficient(
                StreamState.LIQUID, StreamState.GAS_CONDENSATION
            )

            get_overall_heat_transfer_coefficient(
                StreamState.LIQUID_EVAPORATION, StreamState.LIQUID
            )


if __name__ == '__main__':
    unittest.main()
