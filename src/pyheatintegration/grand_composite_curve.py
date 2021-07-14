from collections import defaultdict
from copy import deepcopy

from .stream import Stream, get_temperature_range_streams
from .temperature_range import TemperatureRange, flatten_temperature_ranges


class GrandCompositeCurve:
    """グランドコンポジットカーブを作成するために必要な情報を得るためのクラス。

    Args:
        streams (list[Stream]): 熱交換を行いたい流体。
        minimum_approach_temp_diff (float): 最小接近温度差[℃]。

    Attributes:
        extarnal_streams (list[Stream]): 外部流体。
        minimum_approach_temp_diff (float): 最小接近温度差[℃]。
        temps (list[float]): 温度のリスト[℃]。
        heats (list[float]): 熱量のリスト[W]。
        pinch_points (list[tuple[int, float]]):
            ピンチポイントとなるインデックスと温度のtupleのリスト。
    """

    def __init__(
        self,
        streams_: list[Stream],
        minimum_approach_temp_diff: float
    ):
        streams = deepcopy(streams_)
        self.minimum_approach_temp_diff = minimum_approach_temp_diff

        # 受熱流体は最小接近温度分ずらす。
        for stream in streams:
            if stream.is_cold():
                stream.shift_temperature(self.minimum_approach_temp_diff)

        streams.sort(key=lambda stream: stream.input_temperature())

        self.external_streams = [
            stream for stream in streams if stream.is_external()
        ]

        temp_ranges, temp_range_streams = get_temperature_range_streams([
            stream for stream in streams if stream.is_internal()
        ])
        temp_ranges.sort()

        self.temps = flatten_temperature_ranges(temp_ranges)
        self.heats = _get_heats(temp_ranges, temp_range_streams)

        self.pinch_points = [
            (i, self.temps[i]) for i, heat in enumerate(self.heats) if heat == 0
        ]

    def pinch_point_temp(self) -> float:
        """ピンチポイントの温度を返します。

        ピンチポイントが複数ある場合、最小値を返します。

        Raises:
            RuntimeError: ピンチポイントが求まっていないかピンチポイントが存在しない場合。
        """
        if not self.pinch_points:
            raise RuntimeError('ピンチポイントが求まっていません。')

        return self.pinch_points[0][1]

    def solve_external_heat(self) -> dict[str, float]:
        """外部流体による熱交換量を求めます.

        Returns:
            dict[int, float]: 流体のidごとの交換熱量。

        Raises:
            RuntimeError: ピンチポイントを求める前に呼び出した場合。
        """
        if not self.pinch_points:
            raise RuntimeError('ピンチポイントが求まっていません。')

        hot_streams = self._update_external_streams_heat(
            [stream for stream in self.external_streams if stream.is_hot()],
            self.heats[self.pinch_points[-1][0]:],
            self.temps[self.pinch_points[-1][0]:],
            self.pinch_points[-1][1]
        )

        cold_streams = self._update_external_streams_heat(
            [stream for stream in self.external_streams if stream.is_cold()],
            self.heats[self.pinch_points[0][0]::-1],
            self.temps[self.pinch_points[0][0]::-1],
            self.pinch_points[0][1]
        )

        return {
            stream.id_: stream.heat() for stream in hot_streams + cold_streams
        }

    def _update_external_streams_heat(
        self,
        streams: list[Stream],
        heats: list[float],
        temps: list[float],
        pinch_point_temp: float
    ) -> list[Stream]:
        """外部流体の交換熱量を決定します。

        ピンチポイントが複数ある場合、pinch_point_tempは与熱流体と受熱流体で変わります。与
        熱流体の場合は、ピンチポイントのうち最大温度の点、受熱流体の場合は、ピンチポイントのう
        ち最小温度の点となります。

        Args:
            streams list[Stream]: 流体。
            heats list[float]: 熱量変化。
            temps list[float]: 温度変化。
            pinch_point_temp (float): ピンチポイントの温度。

        Returns:
            list[Stream]: 情報を更新した流体のリスト。
        """
        heated = 0.0
        not_heated = heats[-1]

        streams.sort(key=lambda stream: stream.cost)
        for stream in streams:
            # すでに交換熱量が設定されている場合にはスキップする。
            if stream.heat() != 0:
                continue

            target_temperature = stream.output_temperature()

            # 与熱流体の場合は、出口温度がピンチポイントの温度より低い時、受熱流体の場合は、
            # 出口温度がピンチポイントの温度より高い時、外部流体として用いることができない。
            if (stream.is_hot() and target_temperature < pinch_point_temp) \
               or (stream.is_cold() and target_temperature > pinch_point_temp):
                continue

            for i in range(len(heats)):
                if i == len(heats) - 1:
                    # 与熱流体の場合は、流体温度がtemps[i]よりも大きい時、受熱流体の場合は、
                    # 流体温度がtemps[i]より小さい時、外部流体として用いることができる。
                    if (stream.is_hot() and target_temperature >= temps[i]) \
                       or (stream.is_cold() and target_temperature <= temps[i]):
                        stream.update_heat(not_heated)
                        break
                start_temp = temps[i]
                finish_temp = temps[i + 1]
                temp_range = TemperatureRange(start_temp, finish_temp)
                start_heat = heats[i]
                finish_heat = heats[i + 1]
                if start_heat == finish_heat:
                    continue
                if target_temperature in temp_range:
                    if temp_range.delta != 0:
                        slope = (finish_temp - start_temp) / (finish_heat - start_heat)
                        heat = 1 / slope * (target_temperature - start_temp) + start_heat
                    else:
                        heat = start_heat
                    heat = max(0, min(heat, not_heated))
                    stream.update_heat(heat)
                    heated += heat
                    not_heated -= heat
                    break

        return streams


def _get_heats(
    temp_ranges: list[TemperatureRange],
    temp_range_streams: defaultdict[TemperatureRange, set[Stream]]
) -> list[float]:
    """温度変化領域ごとの熱量変化を求めます。

    Args:
        temp_ranges: list[TemperatureRange]: 温度領域のリスト。
        temp_range_streams defaultdict[TemperatureRange, set[Stream]]:
            温度領域ごとの流体のセット。

    Returns:
        list[float]: 熱量のリスト。
    """
    temp_range_lacking_heat = _get_lacking_heats(temp_range_streams)

    temp_ranges.sort()
    heats = [0.0] * (len(temp_ranges) + 1)
    for i, temp_range in enumerate(temp_ranges):
        heats[i + 1] = heats[i] - temp_range_lacking_heat[temp_range]
    min_heat = min(heats)

    return [heat - min_heat for heat in heats]


def _get_lacking_heats(
    temp_range_streams: defaultdict[TemperatureRange, set[Stream]]
) -> defaultdict[TemperatureRange, float]:
    """温度領域ごとの不足熱量を求めます.

    Args:
        temp_range_streams defaultdict[TemperatureRange, set[Stream]]
            温度領域ごとの流体のセット。

    Returns:
        defaultdict[TemperatureRange, float]: 温度領域ごとの過不足熱量。
    """
    return defaultdict(int, {
        temp_range: sum(s.heat() for s in streams if s.is_hot()) - sum(s.heat() for s in streams if s.is_cold())
        for temp_range, streams in temp_range_streams.items()
    })
