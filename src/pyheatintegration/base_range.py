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


def merge(range_: T, other: T) -> T:
    """範囲を結合します。

    Args:
        range_ (T): 結合元。
        other (T): 結合対象。

    Returns:
        T: 結合後の範囲。

    Raises:
        TypeError: 結合元と結合対象の型が一致しない場合。
        ValueError: 結合可能ではない範囲が渡された場合。
    """
    if type(range_) != type(other):
        raise TypeError(
            f'{repr(range_)}と{repr(other)}は、'
            '型が異なるため、結合することができません。'
        )

    if not range_.mergeable(other):
        raise ValueError(
            f"{repr(range_)}と{repr(other)}は結合することができません。"
            "終了値と結合対象の開始値が同じか、"
            "開始値と結合対象の終了値が同じである必要があります。"
        )

    cls = type(range_)

    if range_.start == other.finish:
        return cls(other.start, range_.finish)
    return cls(range_.start, other.finish)


def is_continuous(
    ranges_: list[T]
) -> Optional[tuple[float, float]]:
    """領域のリストが連続であるかを検証します。

    Args:
        ranges_ (list[T]): 領域のリスト。

    Returns:
        Optional[tuple[float, float]]:
            領域が連続である場合はNoneを返し、連続でない場合は、連続でないと判断された箇所の
            値をタプルで返します。
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


def get_ranges(
    values: list[float],
    cls: type[T]
) -> list[T]:
    """領域のリストを返します。

    Args:
        values (list[float]): 領域の開始値と終了値を構成する値のリスト。
        cls (type[T]): 領域のクラス。HeatRange/TemperatureRange

    Returns:
        list[T]: 領域のリスト。
    """
    values = sorted(values)
    return [cls(values[i], values[i + 1]) for i in range(len(values) - 1)]
