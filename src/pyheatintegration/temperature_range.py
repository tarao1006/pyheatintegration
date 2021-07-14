from __future__ import annotations

from .base_range import BaseRange


class TemperatureRange(BaseRange):

    def merge(self, other: TemperatureRange) -> TemperatureRange:
        """範囲を結合します。

        Args:
            other (TemperatureRange): 結合対象。

        Returns:
            TemperatureRange: 結合後の範囲。

        Examples:
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
                f"{repr(self)}と{repr(other)}は結合することができません。"
                "終了値と結合対象の開始値が同じか、"
                "開始値と結合対象の終了値が同じである必要があります。"
            )

        if self.start == other.finish:
            return TemperatureRange(other.start, self.finish)
        return TemperatureRange(self.start, other.finish)


BaseRange.register(TemperatureRange)


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
