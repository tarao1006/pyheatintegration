import math

from .enums import StreamState
from .heat_range import HeatRange, merge_heat_range
from .plot_segment import PlotSegment

OVERALL_HEAT_TRANSFER_COEFFICIENT = {
    StreamState.LIQUID: {
        StreamState.LIQUID: 300.0,
        StreamState.GAS: 200.0,
        StreamState.LIQUID_EVAPORATION: 1000.0
    },
    StreamState.GAS: {
        StreamState.LIQUID: 200.0,
        StreamState.GAS: 150.0,
        StreamState.LIQUID_EVAPORATION: 500.0
    },
    StreamState.GAS_CONDENSATION: {
        StreamState.LIQUID: 1000.0,
        StreamState.GAS: 500.0,
        StreamState.LIQUID_EVAPORATION: 1500.0
    },
}


def get_overall_heat_transfer_coefficient(
    hot_stream_state: StreamState,
    cold_stream_state: StreamState
) -> float:
    """対応する総括伝熱係数を返します。

    Args:
        hot_stream_state (StreamState): 与熱流体の状態。
        cold_stream_state (StreamState): 受熱流体の状態。

    Returns:
        float: 総括伝熱係数 [W/m2.K]

    Exapmles:
        >>> get_overall_heat_transfer_coefficient(StreamState.LIQUID, StreamState.LIQUID)
        300.0
    """
    if hot_stream_state not in [
        StreamState.LIQUID, StreamState.GAS, StreamState.GAS_CONDENSATION
    ]:
        raise ValueError(
            '与熱流体の状態が不正です。対応する総括伝熱係数が設定されていません。'
            f'状態: {hot_stream_state} '
            '設定可能な状態: '
            f'{StreamState.LIQUID}, '
            f'{StreamState.GAS}, '
            f'{StreamState.GAS_CONDENSATION}'
        )

    if cold_stream_state not in [
        StreamState.LIQUID, StreamState.GAS, StreamState.LIQUID_EVAPORATION
    ]:
        raise ValueError(
            '受熱流体の状態が不正です。対応する総括伝熱係数が設定されていません。'
            f'状態: {cold_stream_state} '
            '設定可能な状態: '
            f'{StreamState.LIQUID}, '
            f'{StreamState.GAS}, '
            f'{StreamState.LIQUID_EVAPORATION}'
        )

    return OVERALL_HEAT_TRANSFER_COEFFICIENT[hot_stream_state][cold_stream_state]


class HeatExchanger:
    """熱交換器を表すクラス。

    Args:
        heat_range (HeatRange): 熱量領域。
        hot_plot_segment (PlotSegment): 与熱流体のプロットセグメント。
        cold_plot_segment (PlotSegment): 受熱流体のプロットセグメント。

    Attributes:
        heat_range (HeatRange): 熱交換の範囲。
        hot_stream_uuid (str): 与熱流体のid。
        cold_stream_uuid (str): 受熱流体のid。
        hot_stream_state (StreamState): 与熱流体の状態。
        cold_stream_state (StreamState): 受熱流体の状態。
        hot_temperature_range (TemperatureRange): 与熱流体の温度領域。
        cold_temperature_range (TemperatureRange): 受熱流体の温度領域。
        lmtd (float): 対数平均温度差。
        hot_plot_segment (PlotSegment): 与熱流体のプロットセグメント。
        cold_plot_segment (PlotSegment): 受熱流体のプロットセグメント。
        reboiler_or_reactor (bool): リボイラーもしくは反応器で用いるか。
    """

    def __init__(
        self,
        heat_range: HeatRange,
        hot_plot_segment: PlotSegment,
        cold_plot_segment: PlotSegment,
        counterflow: bool = True
    ):
        self.heat_range = heat_range
        self.hot_plot_segment = hot_plot_segment
        self.cold_plot_segment = cold_plot_segment
        self.hot_temperature_range = self.hot_plot_segment.temperature_range
        self.cold_temperature_range = self.cold_plot_segment.temperature_range
        self.hot_stream_uuid = self.hot_plot_segment.uuid
        self.cold_stream_uuid = self.cold_plot_segment.uuid
        self.hot_stream_state = self.hot_plot_segment.state
        self.cold_stream_state = self.cold_plot_segment.state
        self.reboiler_or_reactor = self.hot_plot_segment.reboiler_or_reactor | self.cold_plot_segment.reboiler_or_reactor

        if counterflow:
            self.lmtd = self.init_lmtd_counterflow()
        else:
            self.lmtd = self.init_lmtd_pararell_flow()

    def __repr__(self) -> str:
        return (
            'HeatExchanger('
            f'{self.heat_range}, '
            f'{self.hot_plot_segment}, '
            f'{self.cold_plot_segment})'
        )

    def __str__(self) -> str:
        return (
            "HeatExchanger("
            f"{self.heat_range}, "
            f"{self.hot_plot_segment}, "
            f"{self.cold_plot_segment})"
        )

    def __lt__(self, other) -> bool:
        return self.heat_range < other.heat_range

    def init_lmtd_pararell_flow(self) -> float:
        """並流の場合の対数平均温度差を返します。

        並流が不可能な場合はNoneを返します。

        Returns:
            Optional[float]: 並流の場合の対数平均温度差。並流が不可能な場合はNone。
        """
        hot_low_temp, hot_high_temp = self.hot_temperature_range()
        cold_low_temp, cold_high_temp = self.cold_temperature_range()

        start_temp_diff = hot_high_temp - cold_low_temp
        finish_temp_diff = hot_low_temp - cold_high_temp

        if finish_temp_diff <= 0:
            raise RuntimeError(
                '出口温度差が0以下となるため、並流にすることができません。'
                f'出口温度差: {finish_temp_diff} ℃'
            )

        if start_temp_diff == finish_temp_diff:
            return start_temp_diff

        return (start_temp_diff - finish_temp_diff) / math.log(start_temp_diff / finish_temp_diff)

    def init_lmtd_counterflow(self) -> float:
        """向流の場合の対数平均温度差を返します。

        Returns:
            float: 向流の場合の対数平均温度差。
        """
        hot_low_temp, hot_high_temp = self.hot_temperature_range()
        cold_low_temp, cold_high_temp = self.cold_temperature_range()

        start_temp_diff = hot_high_temp - cold_high_temp
        finish_temp_diff = hot_low_temp - cold_low_temp

        if start_temp_diff == finish_temp_diff:
            return start_temp_diff

        return (start_temp_diff - finish_temp_diff) / math.log(start_temp_diff / finish_temp_diff)

    def get_area(self, ignore_unknown: bool = True) -> float:
        try:
            overall_heat_transfer_coefficient = get_overall_heat_transfer_coefficient(
                self.hot_stream_state,
                self.cold_stream_state
            )
            return self.heat_range.delta / self.lmtd / overall_heat_transfer_coefficient
        except Exception as e:
            if ignore_unknown:
                return 1.0
            raise e


def merge_heat_exchangers(heat_exchanger: HeatExchanger, other: HeatExchanger) -> HeatExchanger:
    """熱交換器を結合します。

    Args:
        heat_exchanger (HeatExchange): 熱交換器。
        other (HeatExchanger): 熱交換器(結合対象)。

    Returns:
        HeatExchanger: 結合後の熱交換器。
    """
    heat_range = merge_heat_range(heat_exchanger.heat_range, other.heat_range)
    hot_plot_segment = heat_exchanger.hot_plot_segment.merge(other.hot_plot_segment)
    cold_plot_segment = heat_exchanger.cold_plot_segment.merge(other.cold_plot_segment)

    return HeatExchanger(heat_range, hot_plot_segment, cold_plot_segment)
