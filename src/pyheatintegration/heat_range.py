from __future__ import annotations

from typing import Optional

from .base_range import BaseRange

REL_TOL_DIGIT = 9


class HeatRange(BaseRange):
    def __init__(self, start: float, finish: float):
        super().__init__(start, finish)

    def __repr__(self):
        return f"HeatRange({self.start}, {self.finish})"

    def __contains__(self, temp: float, eps: float = 1e-6) -> bool:
        return self.start - eps <= temp <= self.finish + eps

    def merge(self, other: HeatRange) -> HeatRange:
        """範囲を結合します。

        Args:
            other (HeatRange): 結合対象。

        Returns:
            HeatRange: 結合した範囲。

        Example:
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


def is_continuous(heat_ranges_: list[HeatRange]) -> Optional[tuple[float, float]]:
    """範囲が連続であるかを検証します。

    Args:
        heat_ranges_ (list[HeatRange]): 熱量領域のリスト。

    Returns:
        Optional[tuple[float, float]]: 領域が連続であるか。

    Examples:
        >>> is_continuous([HeatRange(0, 10), HeatRange(10, 20)])
        None
        >>> is_continuous([HeatRange(0, 10), HeatRange(15, 20)])
        (10, 15)
        >>> is_continuous([HeatRange(0, 15), HeatRange(10, 20)])
        (15, 10)
    """
    heat_ranges = sorted(heat_ranges_)
    for i in range(len(heat_ranges)):
        if i != len(heat_ranges) - 1:
            if heat_ranges[i].finish != heat_ranges[i + 1].start:
                return heat_ranges[i].finish, heat_ranges[i + 1].start
    return None


def get_heats(heat_ranges_: list[HeatRange]) -> list[float]:
    """熱量のリストを返します。

    Args:
        heat_ranges_ (list[HeatRange]): 熱量領域のリスト。

    Returns:
        list[float]: 熱量のリスト。

    Examples:
        >>> get_heats([HeatRange(0, 10), HeatRange(10, 20)])
        [0, 10, 20]
    """
    heat_ranges = sorted(heat_ranges_)
    if (values := is_continuous(heat_ranges)) is not None:
        raise ValueError(
            f'終了値と開始値が異なります。'
            f'finish: {values[0]}, '
            f'start: {values[1]}'
        )

    res: list[float] = []
    for i in range(len(heat_ranges)):
        res.append(heat_ranges[i].start)
        if i == len(heat_ranges) - 1:
            res.append(heat_ranges[i].finish)

    return res


def get_detailed_heat_ranges(
    heat_ranges_list: list[list[HeatRange]]
) -> list[HeatRange]:
    """与熱流体と受熱流体を合わせた熱量領域を返します。

    Args:
        plot_segments_list (list[list[PlotSegment]]): 複合線のリスト。

    Returns:
        list[HeatRange]: 熱量領域のリスト。
    """
    heats: set[float] = set()
    for heat_ranges in heat_ranges_list:
        heats |= set(get_heats(heat_ranges))

    return get_heat_ranges(sorted(list(heats)))
