from collections import defaultdict
from copy import deepcopy

from .stream import Stream, get_temperature_range_streams
from .temperature_range import TemperatureRange, get_temperatures


class GrandCompositeCurve:
    """グランドコンポジットカーブを作成するために必要な情報を得るためのクラス。

    Args:
        streams (list[Stream]): 熱交換を行いたい流体。
        minimum_approach_temp_diff (float): 最小接近温度差[℃]。

    Attributes:
        extarnal_streams (list[Stream]): 外部流体。
        minimum_approach_temp_diff (float): 最小接近温度差[℃]。
        maximum_pinch_point_temp (float): 最高温であるピンチポイントの温度[℃]。
        maximum_pinch_point_index (int): 最も温度が高いピンチポイントのインデックス。
        minimum_pinch_point_temp (float): 最低音であるピンチポイントの温度[℃]。
        minimum_pinch_point_index (int): 最も温度が低いピンチポイントのインデックス。
        temps (list[float]): 温度のリスト[℃]。
        heats (list[float]): 熱量のリスト[W]。
        hot_utility_target (float): 必要加熱量[W]。
        cold_utility_target (float): 必要冷却熱量[W]。
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
        self.temps = get_temperatures(temp_ranges)
        self.heats = self._get_heats(
            temp_ranges,
            self._lacking_heats(temp_range_streams)
        )

        pinch_point_info = self._set_pinch_point()
        self.maximum_pinch_point_temp = pinch_point_info[0]
        self.maximum_pinch_point_index = pinch_point_info[1]
        self.minimum_pinch_point_temp = pinch_point_info[2]
        self.minimum_pinch_point_index = pinch_point_info[3]

        self.hot_utility_target = self.heats[-1]
        self.cold_utility_target = self.heats[0]

    def solve_external_heat(self) -> dict[int, float]:
        """外部流体による熱交換量を求めます.

        Returns:
            dict[int, float]:
                流体のidごとの交換熱量。

        Raises:
            RuntimeError: ピンチポイントを求める前に呼び出した場合。
        """
        if not hasattr(self, 'maximum_pinch_point_temp') \
           or not hasattr(self, 'minimum_pinch_point_temp'):
            raise RuntimeError('ピンチポイントが求まっていません。')

        external_cold_streams = [
            stream for stream in self.external_streams if stream.is_cold()
        ]
        external_hot_streams = [
            stream for stream in self.external_streams if stream.is_hot()
        ]

        updated_external_streams = self._update_external_streams(
            external_cold_streams,
            external_hot_streams
        )

        return {
            stream.id_: stream.heat()
            for stream in updated_external_streams
        }

    @classmethod
    def _lacking_heats(
        cls,
        temp_range_streams: defaultdict[TemperatureRange, set[Stream]]
    ) -> defaultdict[TemperatureRange, float]:
        """温度領域ごとの不足熱量を求めます.

        Args:
            temp_range_streams defaultdict[float, set[Stream]]:
                温度領域ごとの流体のセット。

        Returns:
            defaultdict[TemperatureRange, float]: 温度領域ごとの過不足熱量。
        """
        return defaultdict(int, {
            temp_range: sum([s.heat() for s in streams if s.is_hot()]) - sum([s.heat() for s in streams if s.is_cold()])
            for temp_range, streams in temp_range_streams.items()
        })

    @classmethod
    def _get_heats(
        cls,
        temp_ranges: list[TemperatureRange],
        temp_range_lacking_heat: dict[TemperatureRange, float]
    ) -> list[float]:
        """温度変化領域ごとの熱量変化を求めます。

        Args:
            temp_ranges: list[TemperatureRange]: 温度領域のリスト。
            temp_range_lacking_heat: dict[TemperatureRange, float]:
                温度領域ごとの過不足熱量。

        Returns:
            list[float]: 熱量のリスト。
        """
        temp_ranges.sort()
        heats = [0.0] * (len(temp_ranges) + 1)
        for i, temp_range in enumerate(temp_ranges):
            heats[i + 1] = heats[i] - temp_range_lacking_heat[temp_range]
        min_heat = min(heats)

        return [heat - min_heat for heat in heats]

    def _set_pinch_point(self) -> tuple[float, int, float, int]:
        """ピンチポイントとピンチポイントのインデックスを求めます。
        """
        # heat == 0は必ず存在する。
        if 0 not in self.heats:
            raise ValueError("heatに0が存在しません。")

        pinch_point_indexes = [
            i for i, heat in enumerate(self.heats) if heat == 0
        ]
        pinch_points = [self.temps[i] for i in pinch_point_indexes]

        if any(pinch_point_indexes) in [0, len(self.heats) - 1]:
            print("ピンチポイントの値が不正である可能性があります。")

        return (
            pinch_points[-1],
            pinch_point_indexes[-1],
            pinch_points[0],
            pinch_point_indexes[0]
        )

    def _update_external_streams(
            self,
            external_cold_streams: list[Stream],
            external_hot_streams: list[Stream]
    ) -> list[Stream]:
        """外部流体によって交換される熱量を求めます。

        Args:
            external_cold_streams (list[Stream]): 外部受熱流体。
            external_hot_streams (list[Stream]): 外部与熱流体。

        Returns:
            tuple[list[Stream]]:
                交換熱量の情報を追加した外部流体。
        """
        # ピンチポイントの上下に分割し、ピンチポイントに近い順に優先的に熱交換を行わせる。
        heats_heating = self.heats[self.maximum_pinch_point_index:]
        temps_heating = self.temps[self.maximum_pinch_point_index:]
        heats_cooling = self.heats[self.minimum_pinch_point_index::-1]
        temps_cooling = self.temps[self.minimum_pinch_point_index::-1]

        return (
            self._update_external_streams_heat(
                external_hot_streams,
                heats_heating,
                temps_heating,
                self.maximum_pinch_point_temp
            )
            + self._update_external_streams_heat(
                external_cold_streams,
                heats_cooling,
                temps_cooling,
                self.minimum_pinch_point_temp
            )
        )

    def _update_external_streams_heat(
        self,
        streams: list[Stream],
        heats: list[float],
        temps: list[float],
        pinch_point: float
    ) -> list[Stream]:
        """外部流体の交換熱量を決定します。

        Args:
            streams list[Stream]: 流体。
            heats list[float]: 熱量変化。
            temps list[float]: 温度変化。

        Returns:
            list[Stream]: 情報を更新した流体のリスト。
        """
        heated = 0.0
        not_heated = heats[-1]

        streams.sort(
            key=lambda stream: abs(stream.output_temperature() - pinch_point)
        )
        for stream in streams:
            # すでに交換熱量が設定されている場合にはスキップする。
            if stream.heat() != 0:
                continue

            if (stream.is_hot() and stream.output_temperature() < pinch_point) \
               or (stream.is_cold() and stream.output_temperature() > pinch_point):
                continue

            target_temperature = stream.output_temperature()
            for i in range(len(heats)):
                if i == len(heats) - 1:
                    if (stream.is_hot() and target_temperature >= temps[i]) \
                       or (stream.is_cold() and target_temperature <= temps[i]):
                        heat = not_heated
                        stream.update_heat(heat)
                        heated += heat
                        not_heated -= heat
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
