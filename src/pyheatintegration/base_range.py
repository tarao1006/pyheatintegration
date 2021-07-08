from __future__ import annotations

from abc import ABC


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

    def __repr__(self) -> str:
        return f"BaseRange({self.start}, {self.finish})"

    def __str__(self) -> str:
        return f"{self.start}->{self.finish}"

    def __format__(self, format_spec: str) -> str:
        return (
            f"{self.start.__format__(format_spec)}->"
            f"{self.finish.__format__(format_spec)}"
        )

    def __call__(self) -> tuple[float, float]:
        return self.start, self.finish

    def __contains__(self, value: float) -> bool:
        """範囲内にあるかを返します(閉区間)。

        Args:
            value (float): 範囲内にあるかを検証したい値。

        Returns:
            bool: 範囲内にあるかどうか。
        """
        return self.start <= value <= self.finish

    def shift(self, delta: float) -> None:
        """範囲をずらす。

        Args:
            delta (float): ずらす値
        """
        self.start += delta
        self.finish += delta

    def mergeable(self, other: BaseRange) -> bool:
        """結合可能かを返します。

        Args:
            other (BaseRange): 結合対象。

        Returns:
            bool: 結合可能かどうか。
        """
        return self.start == other.finish or self.finish == other.start
