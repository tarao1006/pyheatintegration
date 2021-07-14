from __future__ import annotations

from .base_range import BaseRange, flatten, get_ranges, merge


class TemperatureRange(BaseRange):
    """温度範囲を表すクラス。"""


BaseRange.register(TemperatureRange)


def merge_temperature_range(
    range_: TemperatureRange,
    other: TemperatureRange
) -> TemperatureRange:
    return merge(range_, other)


def get_temperature_ranges(temperatures: list[float]) -> list[TemperatureRange]:
    return get_ranges(temperatures, TemperatureRange)


def flatten_temperature_ranges(temperature_ranges: list[TemperatureRange]) -> list[float]:
    return flatten(temperature_ranges)


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
