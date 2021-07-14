from __future__ import annotations

from abc import ABC
from typing import Optional, TypeVar


def minmax(a: float, b: float) -> tuple[float, float]:
    if a > b:
        return b, a
    return a, b


class BaseRange(ABC):
    """範囲を表すベースクラス。

    Args:
        start (float): 範囲の開始値。
        finish (float): 範囲の終了値。

    Attributes:
        start (float): 範囲の開始値。
        finish (float): 範囲の終了値。
        delta (float): 範囲の大きさ。
    """

    def __init__(self, start: float, finish: float):
        self.start, self.finish = minmax(start, finish)
        self.delta = self.finish - self.start

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.start}, {self.finish})"

    def __str__(self) -> str:
        return f"{self.start}->{self.finish}"

    def __format__(self, format_spec: str) -> str:
        return (
            f"{self.start.__format__(format_spec)}->"
            f"{self.finish.__format__(format_spec)}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseRange):
            return NotImplemented
        return self.start == other.start and self.finish == other.finish

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, BaseRange):
            return NotImplemented
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, BaseRange):
            return NotImplemented
        return self.start < other.start

    def __le__(self, other: object) -> bool:
        if not isinstance(other, BaseRange):
            return NotImplemented
        return self.start <= other.start

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, BaseRange):
            return NotImplemented
        return self.start > other.start

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, BaseRange):
            return NotImplemented
        return self.start >= other.start

    def __hash__(self) -> int:
        return hash((self.start, self.finish))

    def __call__(self) -> tuple[float, float]:
        return self.start, self.finish

    def __contains__(self, value: float) -> bool:
        """範囲内にあるかを返します(閉区間)。

        Args:
            value (float): 範囲内にあるかを検証したい値。

        Returns:
            bool: 範囲内にある場合はTrue、ない場合はFalseを返します。

        Examples:
            >>> base_range = BaseRange(0, 10)
            >>> 10 in base_range
            True
            >>> 11 in base_range
            False
        """
        return self.start <= value <= self.finish

    def shift(self, delta: float) -> None:
        """範囲をずらします。

        Args:
            delta (float): ずらす値。

        Examples:
            >>> base_range = BaseRange(0, 10)
            >>> base_range.shift(10)
            >>> base_range.start
            10
            >>> base_range.finish
            20
        """
        self.start += delta
        self.finish += delta

    def mergeable(self, other: BaseRange) -> bool:
        """結合可能かを返します。

        Args:
            other (BaseRange): 結合対象。

        Returns:
            結合可能であるかどうかを表すbool値。

        Examples:
            >>> base_range = BaseRange(0, 10)
            >>> base_range.mergeable(BaseRange(10, 20))
            True
            >>> base_range.mergeable(BaseRange(5, 20))
            False
        """
        return self.start == other.finish or self.finish == other.start


T = TypeVar('T', bound=BaseRange)


def is_continuous(
    ranges_: list[T]
) -> Optional[tuple[float, float]]:
    """温度領域のリストが連続であるかを検証します。

    Args:
        heat_ranges_ (list[T]): 温度領域のリスト。

    Returns:
        Optional[tuple[float, float]]:
            温度領域が連続である場合はNoneを返し、連続でない場合は、連続でないと判断された箇
            所の値をタプルで返します。

    Examples:
        >>> is_continuous([T(0, 10), T(10, 20)])
        >>> is_continuous([T(0, 10), T(15, 20)])
        (10, 15)
        >>> is_continuous([T(0, 15), T(10, 20)])
        (15, 10)
    """
    ranges = sorted(ranges_)
    for i in range(len(ranges)):
        if i != len(ranges) - 1:
            if ranges[i].finish != ranges[i + 1].start:
                return ranges[i].finish, ranges[i + 1].start
    return None


def flatten(ranges_: list[T]) -> list[float]:
    """領域を平坦化したリストを返します。

    Args:
        heat_ranges_ (list[T]): 領域のリスト。

    Returns:
        list[float]: 平坦化されたリスト。

    Raises:
        ValueError: 領域が連続でない場合。

    Examples:
        >>> get_temperatures([T(0, 10), T(10, 20)])
        [0, 10, 20]
        >>> get_temperatures([T(0, 10), T(30, 40)])
        Traceback (most recent call last):
        ...
        ValueError: 終了値と開始値が異なります。終了値: 10.000 開始値: 30.000
    """
    ranges = sorted(ranges_)
    if (values := is_continuous(ranges)) is not None:
        raise ValueError(
            f'終了値と開始値が異なります。'
            f'終了値: {values[0]:.3f} '
            f'開始値: {values[1]:.3f}'
        )

    res: list[float] = []
    for i in range(len(ranges)):
        res.append(ranges[i].start)
        if i == len(ranges) - 1:
            res.append(ranges[i].finish)

    return res


def get_ranges(values: list[float]) -> list[T]:
    """領域のリストを返します。

    Args:
        temperatures_ (list[float]): 温度のリスト。

    Returns:
        list[T]: 温度領域のリスト。

    Examples:
        >>> get_temperature_ranges([0, 10, 20])
        [T(0, 10), T(10, 20)]
    """
    values = sorted(values)
    return [
        T(values[i], values[i + 1])
        for i in range(len(values) - 1)
    ]
