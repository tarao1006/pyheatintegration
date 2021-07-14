import math
import uuid
from collections import defaultdict
from collections.abc import Iterable
from copy import copy

from .enums import StreamState, StreamType
from .errors import InvalidStreamError
from .temperature_range import (TemperatureRange, get_temperature_ranges,
                                get_temperature_transition)


class Stream:
    r"""熱交換を行う流体を表すクラス。

    Args:
        input_temperature (float): 入り口温度 [℃]。
        output_temperature (float): 出口温度 [℃]。
        heat_flow (float): 熱量 [W]。
        type\_ (StreamType): 流体の種類。
        state (StreamState): 流体の状態。
        cost (float): 流体のコスト [円/J]。外部流体の場合のみ設定可能。
        reboiler_or_reactor (bool): 流体がリボイラーまたは反応器で用いられるかどうか。
        id\_ (str): 流体を区別する識別子。

    Attributes:
        id_ (str): 流体を区別する識別子。
        temperature_range　(TemperatureRange): 温度範囲。
        heat_flow (float): 熱量 [W]。
        cost (float): コスト [円/J]。
        type_ (StreamType): 流体の種類。
        state　(StreamState): 流体の状態。
        reboiler_or_reactor (bool): 流体がリボイラーまたは反応器で用いられるかどうか。

    Raises:
        InvalidStreamError:
            入り口温度と出口温度の大小関係と流体種の関係が不正である場合。また、外部流体の熱
            量が0以外の場合および外部流体以外の流体の熱量が0である場合。外部流体以外にコスト
            を設定した場合。

    Examples:
        >>> Stream(0, 20, 300)
        Stream(0, 20, 300, type_=StreamType.COLD, state=StreamState.UNKNOWN, cost=0.0, reboiler_or_reactor=False, id_="e0c1facb-538b-417f-862c-5cf8043ec075")
        >>> Stream(20, 0, 300)
        Stream(20, 0, 300, type_=StreamType.HOT, state=StreamState.UNKNOWN, cost=0.0, reboiler_or_reactor=False, id_="1a193fc7-9f34-4e6a-8e99-615d40be1b20")
        >>> Stream(0, 0, 0)
        Traceback (most recent call last):
        ...
        InvalidStreamError: 入り口温度と出口温度が同じ流体の種類は明示的に指定する必要があります。
    """

    def __init__(
        self,
        input_temperature: float,
        output_temperature: float,
        heat_flow: float,
        type_: StreamType = StreamType.AUTO,
        state: StreamState = StreamState.UNKNOWN,
        cost: float = 0.0,
        reboiler_or_reactor: bool = False,
        id_: str = ''
    ):
        if id_:
            self.id_ = id_
        else:
            self.id_ = str(uuid.uuid4())

        if type_ == StreamType.AUTO:
            if input_temperature < output_temperature:
                self.type_ = StreamType.COLD
            elif input_temperature > output_temperature:
                self.type_ = StreamType.HOT
            else:
                raise InvalidStreamError(
                    '入り口温度と出口温度が同じ流体の種類は明示的に指定する必要があります。'
                )
        else:
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
                f"入り口温度 [℃]: {input_temperature} "
                f"出口温度 [℃]: {output_temperature}"
            )

        if self.is_hot() and input_temperature < output_temperature:
            raise InvalidStreamError(
                "与熱流体は入り口温度が出口温度より高い必要があります。"
                f"流体の種類: {self.type_.describe()} "
                f"入り口温度 [℃]: {input_temperature} "
                f"出口温度 [℃]: {output_temperature}"
            )

        if self.is_internal() and cost != 0:
            raise InvalidStreamError(
                "外部流体以外にはコストを設定できません。"
                f"流体の種類: {self.type_.describe()} "
                f"コスト [円]: {cost} "
            )

        self.cost = cost
        self.temperature_range = TemperatureRange(
            input_temperature,
            output_temperature
        )
        self.heat_flow = heat_flow

        self.state = state

        if self.state in [StreamState.LIQUID_EVAPORATION, StreamState.GAS_CONDENSATION] \
           and not self.is_isothermal():
            raise InvalidStreamError(
                '相変化によって熱交換を行う流体は等温である必要があります。'
                f'流体の状態: {self.state.describe()} '
                f'入口温度: {input_temperature} '
                f'出口温度: {output_temperature}'
            )

        self.reboiler_or_reactor = reboiler_or_reactor

    def __repr__(self) -> str:
        return (
            f'Stream('
            f'{self.input_temperature()}, '
            f'{self.output_temperature()}, '
            f'{self.heat_flow}, '
            f'type_={self.type_}, '
            f'state={self.state}, '
            f'cost={self.cost}, '
            f'reboiler_or_reactor={self.reboiler_or_reactor}, '
            f'id_="{self.id_}"'
            ')'
        )

    def __str__(self) -> str:
        return (
            f'{self.type_.describe()}, '
            f'input [℃]: {self.input_temperature()}, '
            f'output [℃]: {self.output_temperature()}, '
            f'heat flow [W]: {self.heat_flow}'
        )

    def __format__(self, format_spec: str) -> str:
        description = self.type_.describe()
        return (
            f'{description},{"":{14 - len(description)}s}'
            f'input [℃]: {self.input_temperature().__format__(format_spec)}, '
            f'output [℃]: {self.output_temperature().__format__(format_spec)}, '
            f'heat flow [W]: {self.heat_flow.__format__(format_spec)}'
        )

    def sort_key(self) -> float:
        """ソートの際に用いるキーを返します。

        与熱流体は出口温度、受熱温度は入口温度を返します。

        Returns:
            float: ソート時にキーとなる値。
        """
        if self.is_hot():
            return self.output_temperature()
        return self.input_temperature()

    def is_external(self) -> bool:
        """外部流体であるかを返します。

        Returns:
            bool: 外部流体であるかどうか。
        """
        return self.type_ in [StreamType.EXTERNAL_HOT, StreamType.EXTERNAL_COLD]

    def is_internal(self) -> bool:
        """外部流体以外であるかを返します。

        Returns:
            bool: 外部流体以外であるかどうか。
        """
        return not self.is_external()

    def is_hot(self) -> bool:
        """与熱流体であるかを返します。

        Returns:
            bool: 与熱流体であるかどうか。
        """
        return self.type_ in [StreamType.HOT, StreamType.EXTERNAL_HOT]

    def is_cold(self) -> bool:
        """受熱流体であるかを返します。

        Returns:
            bool: 受熱流体であるかどうか。
        """
        return not self.is_hot()

    def is_isothermal(self) -> bool:
        """等温流体かを返します。

        Returns:
            bool: 等温流体であるかどうか。
        """
        return math.isclose(self.temperature_range.delta, 0.0)

    def input_temperature(self) -> float:
        """入り口温度を返します。

        Returns:
            float: 入り口温度。
        """
        if self.is_hot():
            return self.temperature_range.finish
        return self.temperature_range.start

    def output_temperature(self) -> float:
        """出口温度を返します。

        Returns:
            float: 出口温度。
        """
        if self.is_hot():
            return self.temperature_range.start
        return self.temperature_range.finish

    def temperature(self) -> float:
        """温度変化を返します。

        Returns:
            float: 温度変化 [℃]。
        """
        return self.temperature_range.delta

    def heat(self) -> float:
        """熱量を返します。

        Returns:
            float: 熱量 [W]。
        """
        return self.heat_flow

    def temperatures(self) -> tuple[float, float]:
        """入り口温度と出口温度を返します。

        Returns:
            tuple[float, float]: 温度範囲。
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

        Returns:
            bool: 与えられた温度をとるかどうか。
        """
        return temperature in self.temperature_range

    def contain_temperatures(self, temperatures: Iterable[float]) -> bool:
        """与えられた複数の温度をとるかを返します。

        全ての温度をとる場合のみTrueを返します。

        Args:
            temperatures (list[float]): 検証したい温度のリスト。

        Returns:
            bool: 与えられた複数の温度をとるかどうか。
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
            input_temperature (float): 更新する入り口温度 [℃]。
            output_temperature (float): 更新する出口温度 [℃]。

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


def is_valid_streams(streams: list[Stream]) -> bool:
    """与熱流体および受熱流体がそれぞれ1つ以上含まれるかどうかを返します。

    Args:
        streams (list[Stream]): 流体のリスト。

    Returns:
        bool: 流体のリストが不正かどうか。

    Example:
        >>> is_valid_streams([
                Stream(40, 90, 150),
                Stream(80, 110, 180),
                Stream(125, 80, 160),
                Stream(100, 60, 160)
            ])
        True
        >>> is_valid_streams([
                Stream(40, 90, 150),
                Stream(80, 110, 180)
            ])
        False
    """

    hot_streams = [stream for stream in streams if stream.is_hot()]
    cold_streams = [stream for stream in streams if stream.is_cold()]

    if not hot_streams or not cold_streams:
        return False
    return True


def get_temperature_range_streams(
    streams: list[Stream]
) -> tuple[
    list[TemperatureRange],
    defaultdict[TemperatureRange, set[Stream]]
]:
    """温度領域に属する流体を返します。

    Args:
        streams (list[Stream]): 流体のリスト。

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
    """温度領域ごとに必要な熱量を返します。

    Args:
        streams (list[Stream]): 流体のリスト。

    Returns:
        tuple[list[TemperatureRange], dict[TemperatureRange, float]]:
            温度領域、温度領域ごとの必要熱量。
    """
    temp_ranges, temp_range_streams = get_temperature_range_streams(streams)
    tem_range_heats = {
        temp_range: sum(stream.heat() for stream in temp_range_streams[temp_range])
        for temp_range in temp_ranges
    }
    return temp_ranges, tem_range_heats
