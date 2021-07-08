from __future__ import annotations

import uuid
from collections.abc import Iterable
from typing import Optional

from .heat_range import HeatRange
from .heat_range import is_continuous as is_continuous_heat_ranges
from .temperature_range import TemperatureRange


class PlotSegment:
    uuid: str
    heat_range: HeatRange
    temperature_range: TemperatureRange

    def __init__(
        self,
        start_heat: float = 0.0,
        finish_heat: float = 0.0,
        start_temperature: float = 0.0,
        finish_temperature: float = 0.0,
        uuid_: Optional[str] = None
    ):
        self.heat_range = HeatRange(start_heat, finish_heat)
        self.temperature_range = TemperatureRange(start_temperature, finish_temperature)
        if uuid_ is None:
            self.uuid = str(uuid.uuid4())
        else:
            self.uuid = uuid_

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

    def line(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return (
            (self.heats()[0], self.temperatures()[0]),
            (self.heats()[1], self.temperatures()[1])
        )

    def heats(self) -> tuple[float, float]:
        return self.heat_range()

    def start_heat(self) -> float:
        return self.heat_range.start

    def finish_heat(self) -> float:
        return self.heat_range.finish

    def temperatures(self) -> tuple[float, float]:
        return self.temperature_range()

    def start_temperature(self) -> float:
        return self.temperature_range.start

    def finish_temperature(self) -> float:
        return self.temperature_range.finish

    def contain_heat(self, heat: float) -> bool:
        return heat in self.heat_range

    def contain_heats(self, heats: Iterable[float]) -> bool:
        return all(self.contain_heat(heat) for heat in heats)

    def contain_temperature(self, temperature: float) -> bool:
        return temperature in self.temperature_range

    def temperatures_at_heats(self, heats: tuple[float, float]) -> tuple[float, float]:
        return self.temperature_at_heat(heats[0]), self.temperature_at_heat(heats[1])

    def temperature_at_heat(self, heat: float) -> float:
        if not self.contain_heat(heat):
            raise ValueError('heatを含んでいる必要があります。')

        heat_left, heat_right = self.heat_range()
        temp_left, temp_right = self.temperature_range()

        slope = (temp_right - temp_left) / (heat_right - heat_left)
        return slope * (heat - heat_left) + temp_left

    def heat_at_temperature(self, temperature: float) -> float:
        if not self.contain_temperature(temperature):
            raise ValueError('heatを含んでいる必要があります。')

        heat_left, heat_right = self.heat_range()
        temp_left, temp_right = self.temperature_range()

        slope = (temp_right - temp_left) / (heat_right - heat_left)
        return 1 / slope * (temperature - temp_left) + heat_left

    def shift_heat(self, delta: float) -> None:
        self.heat_range.shift(delta)

    def mergiable(self, other) -> bool:
        return (self.uuid == other.uuid) \
            and (self.finish_heat() == other.start_heat()) \
            and (self.finish_temperature() == other.start_temperature())

    def merge(self, other: PlotSegment) -> PlotSegment:
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
            self.uuid
        )


def temp_diff(segment: PlotSegment, other: PlotSegment) -> tuple[float, float]:
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
                        plot_segment.uuid
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
    return is_continuous_heat_ranges(
        sorted([plot_segment.heat_range for plot_segment in plot_segments])
    )
