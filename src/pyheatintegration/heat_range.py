from __future__ import annotations

from typing import Iterable

from .base_range import BaseRange, flatten

REL_TOL_DIGIT = 9


class HeatRange(BaseRange):

    def __contains__(self, temp: float, eps: float = 1e-6) -> bool:
        return self.start - eps <= temp <= self.finish + eps

    def merge(self, other: HeatRange) -> HeatRange:
        """範囲を結合します。

        Args:
            other (HeatRange): 結合対象。

        Returns:
            HeatRange: 結合後の範囲。

        Examples:
            >>> a = HeatRange(0, 10)
            >>> b = HeatRange(10, 20)
            >>> a.merge(b)
            HeatRange(0, 20)
            >>> a = HeatRange(10, 20)
            >>> b = HeatRange(0, 10)
            >>> a.merge(b)
            HeatRange(0, 20)

        Raises:
            ValueError: 結合可能ではない範囲が渡された場合。
        """
        if not self.mergeable(other):
            raise ValueError(
                f"{repr(self)}と{repr(other)}は結合することができません。"
                "終了値と結合対象の開始値が同じか、"
                "開始値と結合対象の終了値が同じである必要があります。"
            )

        if self.start == other.finish:
            return HeatRange(other.start, self.finish)
        return HeatRange(self.start, other.finish)


BaseRange.register(HeatRange)


def get_heat_ranges(heats_: list[float]) -> list[HeatRange]:
    """熱量領域のリストを返します。

    Args:
        heats_ (list[float]): 熱量のリスト。

    Returns:
        list[HeatRange]: 熱量領域のリスト。

    Examples:
        >>> get_heat_ranges([0, 10, 20])
        [HeatRange(0, 10), HeatRange(10, 20)]
    """
    heats = sorted(heats_)
    return [
        HeatRange(heats[i], heats[i + 1])
        for i in range(len(heats) - 1)
    ]


def get_merged_heat_ranges(
    heat_ranges_list: Iterable[list[HeatRange]]
) -> list[HeatRange]:
    """複数の熱量領域のリストを合わせた熱量領域を返します。

    Args:
        plot_segments_list (Iterable[list[PlotSegment]]):
            熱量領域のリストのイテラブル。

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
        heats |= set(flatten(heat_ranges))

    return get_heat_ranges(sorted(list(heats)))
