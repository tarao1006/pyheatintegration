from __future__ import annotations

import uuid
from collections.abc import Iterable
from typing import Optional

from .base_range import is_continuous as is_continuous_ranges
from .enums import StreamState
from .heat_range import HeatRange
from .line import Line
from .temperature_range import TemperatureRange


class PlotSegment:
    """プロットの一部を表すクラスです。

    Args:
        start_heat (float): 熱量の開始値。
        finish_heat (float): 熱量の終了値。
        start_temperature (float): 温度の開始値。
        finish_temperature (float): 温度の終了値。
        uuid_ (Optional[str]): uuid。対応する流体がある場合はそのid。
        state (StreamState): 対応する流体の状態。
        reboiler_or_reactor (bool): 対応する流体がリボイラーもしくは反応器で用いられるか。

    Attributes:
        heat_range (HeatRange): 熱量領域。
        temperature_range (TemperatureRange): 温度領域。
        uuid (str): uuid。対応する流体がある場合はそのid。
        state (StreamState): 対応する流体の状態。
        reboiler_or_reactor (bool): 対応する流体がリボイラーもしくは反応器で用いられるか。
    """

    def __init__(
        self,
        start_heat: float = 0.0,
        finish_heat: float = 0.0,
        start_temperature: float = 0.0,
        finish_temperature: float = 0.0,
        uuid_: Optional[str] = None,
        state: StreamState = StreamState.UNKNOWN,
        reboiler_or_reactor: bool = False
    ):
        self.heat_range = HeatRange(start_heat, finish_heat)
        self.temperature_range = TemperatureRange(start_temperature, finish_temperature)
        if uuid_ is None:
            self.uuid = str(uuid.uuid4())
        else:
            self.uuid = uuid_

        self.state = state
        self.reboiler_or_reactor = reboiler_or_reactor

    def __str__(self) -> str:
        return (
            f"heat: ({self.heat_range.start}; "
            f"{self.heat_range.finish}) "
            f"temperature: ({self.temperature_range.start}; "
            f"{self.temperature_range.finish})"
        )

    def __repr__(self) -> str:
        return (
            f"PlotSegment("
            f"{self.heat_range.start}, "
            f"{self.heat_range.finish}, "
            f"{self.temperature_range.start}, "
            f"{self.temperature_range.finish})"
        )

    def __format__(self, format_spec: str) -> str:
        return (
            f"PlotSegment("
            f"{self.heat_range.start.__format__(format_spec)}, "
            f"{self.heat_range.finish.__format__(format_spec)}, "
            f"{self.temperature_range.start}, "
            f"{self.temperature_range.finish})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlotSegment):
            return NotImplemented
        return self.heat_range == other.heat_range \
            and self.temperature_range == other.temperature_range

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, PlotSegment):
            return NotImplemented
        return self.heat_range < other.heat_range

    def __le__(self, other: object) -> bool:
        if not isinstance(other, PlotSegment):
            return NotImplemented
        return self.heat_range <= other.heat_range

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, PlotSegment):
            return NotImplemented
        return self.heat_range > other.heat_range

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, PlotSegment):
            return NotImplemented
        return self.heat_range >= other.heat_range

    def line(self) -> Line:
        """直線の始点と終点を返します。

        Returns:
            Line: 直線。
        """
        return (
            (self.heats()[0], self.temperatures()[0]),
            (self.heats()[1], self.temperatures()[1])
        )

    def heats(self) -> tuple[float, float]:
        """熱量の開始値と終了値を返します。

        Returns:
            tuple[float, float]: 熱量の開始値と終了値。
        """
        return self.heat_range()

    def start_heat(self) -> float:
        """熱量の開始値を返します。

        Returns:
            float: 熱量の開始値。
        """
        return self.heat_range.start

    def finish_heat(self) -> float:
        """熱量の終了値を返します。

        Returns:
            float: 熱量の終了値。
        """
        return self.heat_range.finish

    def temperatures(self) -> tuple[float, float]:
        """温度の開始値と終了値を返します。

        Returns:
            tuple[float, float]: 温度の開始値と終了値。
        """
        return self.temperature_range()

    def start_temperature(self) -> float:
        """温度の開始値を返します。

        Returns:
            float: 温度の開始値。
        """
        return self.temperature_range.start

    def finish_temperature(self) -> float:
        """温度の終了値を返します。

        Returns:
            float: 温度の終了値。
        """
        return self.temperature_range.finish

    def contain_heat(self, heat: float) -> bool:
        """熱量を含むかを返します。

        Args:
            heat (float): 含むかを検証する熱量。

        Returns:
            bool: 熱量を含むかどうか。
        """
        return heat in self.heat_range

    def contain_heats(self, heats: Iterable[float]) -> bool:
        """複数の熱量を含むかを返します。

        Args:
            heats (Iterable[float]): 含むかを検証する熱量。

        Returns:
            bool: 複数の熱量を含むかどうか。
        """
        return all(self.contain_heat(heat) for heat in heats)

    def contain_temperature(self, temperature: float) -> bool:
        """温度を含むかを返します。

        Args:
            temperature (float): 含むかを検証する温度。

        Returns:
            bool: 温度を含むかどうか。
        """
        return temperature in self.temperature_range

    def temperatures_at_heats(self, heats: tuple[float, float]) -> tuple[float, float]:
        """ある複数の熱量をとる温度を返します。

        Args:
            heats (tuple[float, float]): 温度を求めたい熱量。

        Returns:
            tuple[float, float]: ある熱量をとる温度。
        """
        return self.temperature_at_heat(heats[0]), self.temperature_at_heat(heats[1])

    def temperature_at_heat(self, heat: float) -> float:
        """ある熱量をとる温度を返します。

        Args:
            heat (float): 温度を求めたい熱量。

        Returns:
            float: ある熱量をとる温度。
        """
        if not self.contain_heat(heat):
            raise ValueError('heatを含んでいる必要があります。')

        heat_left, heat_right = self.heat_range()
        temp_left, temp_right = self.temperature_range()

        slope = (temp_right - temp_left) / (heat_right - heat_left)
        return slope * (heat - heat_left) + temp_left

    def heat_at_temperature(self, temperature: float) -> float:
        """ある温度をとる熱量を返します。

        Args:
            temperature (float): 熱量を求めたい温度。

        Returns:
            float: ある温度をとる熱量。
        """
        if not self.contain_temperature(temperature):
            raise ValueError('temperatureを含んでいる必要があります。')

        heat_left, heat_right = self.heat_range()
        temp_left, temp_right = self.temperature_range()

        slope = (temp_right - temp_left) / (heat_right - heat_left)
        return 1 / slope * (temperature - temp_left) + heat_left

    def shift_heat(self, delta: float) -> None:
        """熱量をずらします。

        Args:
            delta (float): ずらす値。
        """
        self.heat_range.shift(delta)

    def mergiable(self, other: PlotSegment) -> bool:
        """プロットセグメントを結合可能かを返します。

        Args:
            other (PlotSegment): 結合できるかを検証したいプロットセグメント。

        Returns:
            bool: 結合可能かどうか。
        """
        return (self.uuid == other.uuid) \
            and (self.finish_heat() == other.start_heat()) \
            and (self.finish_temperature() == other.start_temperature())

    def merge(self, other: PlotSegment) -> PlotSegment:
        """プロットセグメントを結合します。

        Args:
            other (PlotSegment): 結合したいプロットセグメント。

        Returns:
            PlotSegment: 結合後のプロットセグメント。
        """
        if self.finish_heat() != other.start_heat():
            raise ValueError("other's start_heat must be self's finish_heat.")
        if self.finish_temperature() != other.start_temperature():
            raise ValueError("other's start_temperature must be self's finish_temperature.")
        if self.uuid != other.uuid:
            raise ValueError("other's uuid must be self's uuid.")

        return PlotSegment(
            self.start_heat(),
            other.finish_heat(),
            self.start_temperature(),
            other.finish_temperature(),
            self.uuid,
            self.state,
            self.reboiler_or_reactor
        )


def temp_diff(segment: PlotSegment, other: PlotSegment) -> tuple[float, float]:
    """同じ熱量領域のプロットセグメントの入り口温度の差と出口温度の差を求める。

    Args:
        segment (PlotSegment): プロットセグメント。
        ohter (PlotSegment): プロットセグメント。

    Returns:
        tuple[float, float]: 入り口温度差、出口温度差。
    """
    hot_temp_start, hot_temp_finish = segment.temperatures()
    cold_temp_start, cold_temp_finish = other.temperatures()

    return (
        hot_temp_start - cold_temp_start,
        hot_temp_finish - cold_temp_finish
    )


def get_plot_segments(
    heat_ranges: list[HeatRange],
    plot_segments: list[PlotSegment]
) -> list[PlotSegment]:
    """指定された熱量領域のプロットセグメントを返す。

    Args:
        heats (list[float]): 熱量変化。
        temps (list[float]): 温度変化。
        heat_ranges (list[HeatRange]): 熱量領域のリスト。

    Returns:
        list[PlotSegment]: プロットセグメントのリスト。
    """
    res: list[PlotSegment] = []
    for heat_range in heat_ranges:
        for plot_segment in plot_segments:
            if plot_segment.contain_heats(heat_range()):
                res.append(
                    PlotSegment(
                        *heat_range(),
                        *plot_segment.temperatures_at_heats(heat_range()),
                        plot_segment.uuid,
                        plot_segment.state,
                        plot_segment.reboiler_or_reactor
                    )
                )
    return res


def is_continuous(
    plot_segments: list[PlotSegment]
) -> Optional[tuple[float, float]]:

    """プロットセグメントが連続であるかを検証します。

    連続であった場合はNoneを返し、連続でなかった場合は、連続ではない箇所の熱量を返します。

    Args:
        plot_segments (list[PlotSegment]): プロットセグメントのリスト。

    Returns:
        Optional[tuple[float, float]]: 領域が連続であるか。
    """
    return is_continuous_ranges(
        sorted([plot_segment.heat_range for plot_segment in plot_segments])
    )
