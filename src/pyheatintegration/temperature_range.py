from __future__ import annotations

from typing import Optional

from .base_range import BaseRange


class TemperatureRange(BaseRange):
    def __init__(self, start: float, finish: float):
        super().__init__(start, finish)

    def __repr__(self) -> str:
        return f"TemperatureRange({self.start}, {self.finish})"

    def merge(self, other: TemperatureRange) -> TemperatureRange:
        """範囲を結合します。

        Args:
            other (TemperatureRange): 結合対象。

        Returns:
            TemperatureRange: 結合した範囲。

        Example:
            >>> a = TemperatureRange(0, 10)
            >>> b = TemperatureRange(10, 20)
            >>> a.merge(b)
            TemperatureRange(0, 20)
            >>> a = TemperatureRange(10, 20)
            >>> b = TemperatureRange(0, 10)
            >>> a.merge(b)
            TemperatureRange(0, 20)

        Raises:
            ValueError: 結合可能ではない範囲が渡された場合。
        """
        if not self.mergeable(other):
            raise ValueError(
                "終了値と結合対象の開始値が同じか、"
                "開始値と結合対象の終了値が同じである必要があります。"
            )

        if self.start == other.finish:
            return TemperatureRange(other.start, self.finish)
        return TemperatureRange(self.start, other.finish)


BaseRange.register(TemperatureRange)


def is_continuous(temp_ranges_: list[TemperatureRange]) -> Optional[tuple[float, float]]:
    """範囲が連続であるかを検証します。

    Args:
        temp_ranges_ (list[HeatRange]): 温度領域のリスト。

    Returns:
        Optional[tuple[float, float]]: 領域が連続であるか。
    """
    temp_ranges = sorted(temp_ranges_)
    for i in range(len(temp_ranges)):
        if i != len(temp_ranges) - 1:
            if temp_ranges[i].finish != temp_ranges[i + 1].start:
                return temp_ranges[i].finish, temp_ranges[i + 1].start
    return None


def get_temperatures(temp_ranges_: list[TemperatureRange]) -> list[float]:
    """温度のリストを返します。

    Args:
        heat_ranges_ (list[TemperatureRange]): 温度領域のリスト。

    Returns:
        list[float]: 温度のリスト。

    Examples:
        >>> get_heats([TemperatureRange(0, 10), TemperatureRange(10, 20)])
        [0, 10, 20]
    """
    temp_ranges = sorted(temp_ranges_)
    if (values := is_continuous(temp_ranges)) is not None:
        raise ValueError(
            f'終了値と開始値が異なります。'
            f'finish: {values[0]}, '
            f'start: {values[1]}'
        )
    res: list[float] = []
    for i in range(len(temp_ranges)):
        if i != len(temp_ranges) - 1:
            if temp_ranges[i].finish != temp_ranges[i + 1].start:
                raise ValueError(
                    f'終了値と開始値が異なります。'
                    f'finish: {temp_ranges[i].finish}, '
                    f'start: {temp_ranges[i + 1].start}'
                )

        res.append(temp_ranges[i].start)
        if i == len(temp_ranges) - 1:
            res.append(temp_ranges[i].finish)

    return res


def get_temperature_ranges(temperatures_: list[float]) -> list[TemperatureRange]:
    """温度領域のリストを返します。

    Args:
        temperatures_ (list[float]): 温度のリスト。

    Returns:
        list[HeatRange]: 温度領域のリスト。

    Examples:
        >>> get_temperature_ranges([0, 10, 20])
        [TemperatureRange(0, 10), TemperatureRange(10, 20)]
    """
    temperatures = sorted(temperatures_)
    return [
        TemperatureRange(temperatures[i], temperatures[i + 1])
        for i in range(len(temperatures) - 1)
    ]


def get_temperature_transition(
    temperature_ranges: list[TemperatureRange]
) -> list[float]:
    """単調増加となるような温度の推移を返します。

    Args:
        temperature_ranges (list[TemperatureRange]): 温度領域のリスト。

    Returns:
        list[float]: 温度の推移。

    Examples:
        >>> temperature_ranges = [
                TemperatureRange(0, 10),
                TemperatureRange(20, 50),
                TemperatureRange(30, 30),
                TemperatureRange(40, 70),
                TemperatureRange(70, 70)
                TemperatureRange(70, 70)
            ]
        >>> sorted(get_temperature_transition(temperature_ranges))
        [0, 10, 20, 30, 30, 40, 50, 70, 70]
    """
    temperatures_set: set[float] = set()

    for temperature_range in temperature_ranges:
        if temperature_range.delta == 0:
            continue
        temperatures_set |= set(temperature_range())

    temperatures = list(temperatures_set)

    for temperature_range in temperature_ranges:
        if temperature_range.delta != 0:
            continue
        temp = temperature_range.start
        temp_count = temperatures.count(temp)
        if temp_count == 0:
            temperatures.extend([temp, temp])
        elif temp_count == 1:
            temperatures.extend([temp])
        elif temp_count == 2:
            # 二つ含まれる場合は何もしない。
            pass
        else:
            raise ValueError(f'同じ値が3つ以上含まれます。値: {temp_count}')

    return temperatures


def accumulate_heats(
    temperature_ranges_: list[TemperatureRange],
    temperature_range_heats: dict[TemperatureRange, float]
) -> list[float]:
    """温度領域ごとの必要熱量から全体で必要な熱量を求めます。

    Args:
        temperature_ranges_ (list[TemperatureRange]): 温度領域のリスト。
        temperature_range_heats (dict[TemperatureRange, float]):
            温度領域ごとの必要熱量。

    Returns:
        list[float]: 温度領域ごとの必要熱量を集計した結果。
    """
    temperature_ranges = sorted(temperature_ranges_)
    if temperature_ranges != (keys := sorted(list(temperature_range_heats.keys()))):
        raise ValueError(
            'temperature_range_heatsが不正です。'
            f'必要なキー: {temperature_ranges} '
            f'存在するキー: {keys}'
        )

    heats = [0.0] * (len(temperature_ranges) + 1)
    for i, temp_range in enumerate(temperature_ranges):
        heats[i + 1] = heats[i] + temperature_range_heats[temp_range]

    return heats
