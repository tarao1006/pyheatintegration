import math
from collections import defaultdict
from collections.abc import Iterable
from copy import copy

from .enums import StreamType
from .errors import InvalidStreamError
from .temperature_range import (TemperatureRange, get_temperature_ranges,
                                get_temperature_transition)


class Stream:

    def __init__(
        self,
        input_temperature: float,
        output_temperature: float,
        heat_flow: float,
        type_: StreamType,
        cost: float = 0.0
    ):
        """流体を表すクラス。

        Args:
            input_temperature (float): 入り口温度
            output_temperature (float): 出口温度
            heat_flow (float): 熱量
            type_ (StreamType): 流体種
            cost (float, optional): 流体のコスト。外部流体の場合のみ設定できる。

        Raises:
            InvalidStreamError:
                入り口温度と出口温度の大小関係と流体種の関係が不正である場合。また、外部流体
                の熱量が0以外の場合、および外部流体以外の流体の熱量が0である場合。
        """
        self.id_ = 0
        self.type_ = type_

        if self.is_internal() and heat_flow == 0:
            raise InvalidStreamError(
                "外部流体でない流体の熱量の入力値は0でない必要があります。"
                f"流体の種類: {self.type_.describe()} 熱量: {heat_flow}"
            )

        if self.is_external() and heat_flow != 0:
            raise InvalidStreamError(
                "外部流体の熱量の入力値は0である必要があります。"
                f"流体の種類: {self.type_.describe()} 熱量: {heat_flow}"
            )

        if self.is_cold() and input_temperature > output_temperature:
            raise InvalidStreamError(
                "受熱流体は入り口温度が出口温度より低い必要があります。"
                f"流体の種類: {self.type_.describe()} "
                f"入り口温度: {input_temperature} "
                f"出口温度: {output_temperature}"
            )

        if self.is_hot() and input_temperature < output_temperature:
            raise InvalidStreamError(
                "与熱流体は入り口温度が出口温度より高い必要があります。"
                f"流体の種類: {self.type_.describe()} "
                f"入り口温度: {input_temperature} "
                f"出口温度: {output_temperature}"
            )

        if self.is_internal() and cost != 0:
            raise InvalidStreamError(
                "外部流体以外にはコストを設定できません。"
                f"流体の種類: {self.type_.describe()} "
                f"コスト: {cost} "
            )

        self.cost = cost
        self.temperature_range = TemperatureRange(
            input_temperature,
            output_temperature
        )
        self.heat_flow = heat_flow

    def __repr__(self) -> str:
        return (
            f"Stream({self.input_temperature()}, "
            f"{self.output_temperature()}, "
            f"{self.heat_flow}, "
            f"{self.type_}, "
            f"{self.cost})"
        )

    def __str__(self) -> str:
        return (
            f"{self.type_.describe()}, "
            f"input [℃]: {self.input_temperature()}, "
            f"output [℃]: {self.output_temperature()}, "
            f"heat flow [W]: {self.heat_flow}"
        )

    def __format__(self, format_spec: str) -> str:
        description = self.type_.describe()
        return (
            f"{description},{'':{14 - len(description)}s}"
            f"input [℃]: {self.input_temperature().__format__(format_spec)}, "
            f"output [℃]: {self.output_temperature().__format__(format_spec)}, "
            f"heat flow [W]: {self.heat_flow.__format__(format_spec)}"
        )

    def set_id(self, id_: int) -> None:
        """流体にidを設定する。

        Args:
            id_ (int): 設定するid。

        Raises:
            ValueError: idが0以下であった場合。
        """
        if id_ <= 0:
            raise ValueError('idは0より大きい必要があります。')
        self.id_ = id_

    def is_external(self) -> bool:
        """外部流体であるかを返します。
        """
        return self.type_ in [StreamType.EXTERNAL_HOT, StreamType.EXTERNAL_COLD]

    def is_internal(self) -> bool:
        """外部流体以外であるかを返します。
        """
        return not self.is_external()

    def is_hot(self) -> bool:
        """与熱流体であるかを返します。
        """
        return self.type_ in [StreamType.HOT, StreamType.EXTERNAL_HOT]

    def is_cold(self) -> bool:
        """受熱流体であるかを返します。
        """
        return not self.is_hot()

    def is_isothermal(self) -> bool:
        """温度変化がない流体かを返します。
        """
        return math.isclose(self.temperature_range.delta, 0.0)

    def input_temperature(self) -> float:
        """入り口温度を返します。
        """
        if self.is_hot():
            return self.temperature_range.finish
        return self.temperature_range.start

    def output_temperature(self) -> float:
        """出口温度を返します。
        """
        if self.is_hot():
            return self.temperature_range.start
        return self.temperature_range.finish

    def temperature(self) -> float:
        """温度変化を返します。
        """
        return self.temperature_range.delta

    def heat(self) -> float:
        """熱量を返します。
        """
        return self.heat_flow

    def temperatures(self) -> tuple[float, float]:
        """入り口温度と出口温度を返します。
        """
        return self.temperature_range()

    def shift_temperature(self, delta: float) -> None:
        """入り口温度と出口温度をずらします。

        Args:
            delta (float): ずらす値。
        """
        self.temperature_range.shift(delta)

    def contain_temperature(self, temperature: float) -> bool:
        """与えられた温度をとるかを返します。

        Args:
            temperature (float): 検証したい温度。
        """
        return temperature in self.temperature_range

    def contain_temperatures(self, temperatures: Iterable[float]) -> bool:
        """与えられた複数の温度をとるかを返します。

        全ての温度をとる場合のみTrueを返します。

        Args:
            temperatures (list[float]): 検証したい温度のリスト。
        """
        return all(map(lambda t: t in self.temperature_range, temperatures))

    def update_temperature(
        self,
        input_temperature: float,
        output_temperature: float
    ) -> None:
        """入り口温度と出口温度を更新します。

        等温流体に対しては呼び出せません。温度の値に加えて、熱量の値を元々の温度変化と新たな温
        度変化の比に従って更新します。

        Args:
            input_temperature (float): 更新する入り口温度。
            output_temperature (float): 更新する出口温度。

        Raises:
            ValueError: 等温流体に対して温度を更新しようとした場合。
        """
        if self.is_isothermal():
            raise ValueError("等温流体は入り口温度・出口温度を変更できません。")

        old_temp_delta = self.temperature_range.delta
        self.temperature_range = TemperatureRange(input_temperature, output_temperature)

        self.heat_flow = self.heat() * self.temperature_range.delta / old_temp_delta

    def update_heat(self, heat_flow: float) -> None:
        """熱量を更新します。

        入り口温度と出口温度が異なる流体に対しては呼び出せません。

        Args:
            heat_flow (float): 更新する熱量。

        Raises:
            ValueError: 等温流体以外に対して熱量を更新しようとした場合。
        """
        if self.is_internal() and not self.is_isothermal():
            raise ValueError("非等温流体は入り口温度・出口温度を変更せずに熱量を変更できません。")

        self.heat_flow = heat_flow


def get_temperature_range_streams(
    streams: list[Stream]
) -> tuple[
    list[TemperatureRange],
    defaultdict[TemperatureRange, set[Stream]]
]:
    """温度領域と、温度領域に属する流体を返します。

    Args:
        streams (list[Stream]): 流体。

    Returns:
            list[list[TemperatureRange], defaultdict[TemperatureRange, set[Stream]]:
                温度領域、温度領域に属する流体。
    """
    temperatures = sorted(get_temperature_transition([
        stream.temperature_range for stream in streams
    ]))
    temp_ranges = sorted(get_temperature_ranges(temperatures))

    temp_streams: defaultdict[float, set[Stream]] = defaultdict(set)
    for temperature in temperatures:
        for stream in streams:
            if stream.contain_temperature(temperature):
                temp_streams[temperature].add(stream)

    temp_range_streams: defaultdict[TemperatureRange, set[Stream]] = defaultdict(set)
    for temp_range in temp_ranges:
        target_streams = temp_streams[temp_range.start] & temp_streams[temp_range.finish]

        # 温度変化が0の領域の場合、温度変化がある流体を除く
        if temp_range.delta == 0:
            target_streams -= set(stream for stream in target_streams if not stream.is_isothermal())

        for target_stream in target_streams:
            stream = copy(target_stream)
            if not stream.is_isothermal():
                stream.update_temperature(temp_range.start, temp_range.finish)
            temp_range_streams[temp_range].add(stream)

    return temp_ranges, temp_range_streams


def get_temperature_range_heats(
    streams: list[Stream]
) -> tuple[list[TemperatureRange], dict[TemperatureRange, float]]:
    temp_ranges, temp_range_streams = get_temperature_range_streams(streams)
    tem_range_heats = {
        temp_range: sum(stream.heat() for stream in temp_range_streams[temp_range])
        for temp_range in temp_ranges
    }
    return temp_ranges, tem_range_heats
