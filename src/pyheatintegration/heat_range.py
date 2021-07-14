from __future__ import annotations

from typing import Iterable

from .base_range import BaseRange, is_continuous

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


# def is_continuous(
#     heat_ranges_: list[HeatRange]
# ) -> Optional[tuple[float, float]]:
#     """熱量領域のリストが連続であるかを検証します。

#     Args:
#         heat_ranges_ (list[HeatRange]): 熱量領域のリスト。

#     Returns:
#         Optional[tuple[float, float]]:
#             熱量領域が連続である場合はNoneを返し、連続でない場合は、連続でないと判断された箇
#             所の値をタプルで返します。

#     Examples:
#         >>> is_continuous([HeatRange(0, 10), HeatRange(10, 20)])
#         >>> is_continuous([HeatRange(0, 10), HeatRange(15, 20)])
#         (10, 15)
#         >>> is_continuous([HeatRange(0, 15), HeatRange(10, 20)])
#         (15, 10)
#     """
#     heat_ranges = sorted(heat_ranges_)
#     for i in range(len(heat_ranges)):
#         if i != len(heat_ranges) - 1:
#             if heat_ranges[i].finish != heat_ranges[i + 1].start:
#                 return heat_ranges[i].finish, heat_ranges[i + 1].start
#     return None


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
            f'終了値と開始値が異なり、領域が連続でない箇所があります。'
            f'終了値: {values[0]:.3f} '
            f'開始値: {values[1]:.3f}'
        )

    res: list[float] = []
    for i in range(len(heat_ranges)):
        res.append(heat_ranges[i].start)
        if i == len(heat_ranges) - 1:
            res.append(heat_ranges[i].finish)

    return res


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
        heats |= set(get_heats(heat_ranges))

    return get_heat_ranges(sorted(list(heats)))
