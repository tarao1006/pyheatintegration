from __future__ import annotations

from .base_range import BaseRange, flatten, get_ranges, merge

REL_TOL_DIGIT = 9


class HeatRange(BaseRange):
    """熱量範囲を表すクラス。"""

    def __contains__(self, temp: float, eps: float = 1e-6) -> bool:
        return self.start - eps <= temp <= self.finish + eps


BaseRange.register(HeatRange)


def merge_heat_range(range_: HeatRange, other: HeatRange) -> HeatRange:
    return merge(range_, other)


def get_heat_ranges(heats: list[float]) -> list[HeatRange]:
    return get_ranges(heats, HeatRange)


def flatten_heat_ranges(heat_ranges: list[HeatRange]) -> list[float]:
    return flatten(heat_ranges)


def get_merged_heat_ranges(
    heat_ranges_list: list[list[HeatRange]]
) -> list[HeatRange]:
    """複数の熱量領域のリストを合わせた熱量領域を返します。

    Args:
        plot_segments_list (list[list[PlotSegment]]):
            熱量領域のリストのリスト。

    Returns:
        list[HeatRange]: 結合後の熱量領域のリスト。

    Examples:
        >>> l1 = [HeatRange(0, 10), HeatRange(10, 30)]
        >>> l2 = [HeatRange(5, 15), HeatRange(15, 40)]
        >>> get_merged_heat_ranges([l1, l2])
        [HeatRange(0, 5), HeatRange(5, 10), HeatRange(10, 15), HeatRange(15, 30), HeatRange(30, 40)]
    """
    heats: set[float] = set()
    for heat_ranges in heat_ranges_list:
        heats |= set(flatten_heat_ranges(heat_ranges))

    return get_heat_ranges(sorted(list(heats)))
