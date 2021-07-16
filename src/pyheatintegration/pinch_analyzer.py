import math
from copy import deepcopy

from .grand_composite_curve import GrandCompositeCurve
from .heat_exchanger import HeatExchanger
from .heat_range import HeatRange, get_merged_heat_ranges
from .line import Line
from .plot_segment import PlotSegment, get_plot_segments
from .stream import Stream, is_valid_streams
from .tq_diagram import TQDiagram, get_possible_minimum_temp_diff_range


def calculate_heat_exchanger_cost(
    area: float,
    reboiler_or_reactor: bool = False
) -> float:
    """熱交換器にかかるコストを返します。

    Args:
        area (float): 熱交換器の面積。
        k (float): 係数。リボイラーまたは反応器の場合は2

    Returns:
        float: コスト[円]。
    """
    if reboiler_or_reactor:
        k = 2.0
    else:
        k = 1.0
    return 1_500_000 * math.pow(area, 0.65) * k


class PinchAnalyzer:
    """流体のリストと最小接近温度差を設定し、グランドコンポジットカーブおよびTQ線図を作成します。

    解析を行う場合はこのクラス経由で扱います。このクラスを経由することで、流体のidが重複してい
    ないことや、最小接近温度差が指定可能な値であるかを検証したのちに図を作成するため、予想外の
    エラーが生じることを回避することができます。

    Args:
        streams_ (list[Stream]): 流体のリスト。
        minimum_approach_temp_diff (float): 最小接近温度差 [℃]。
        ignore_maximum (bool): 最小接近温度差の最大値のチェックを無視するかどうか。

    Attributes:
        gcc (GrandCompositeCurve): グランドコンポジットカーブ。
        tq (TQDiagram): TQ線図。
        streams (list[Stream]): 流体のリスト。
        minimum_approach_temp_diff_range (TemperatureRange): 最小接近温度差の指定可能範囲。
        pinch_point_temp (float): ピンチポイントの温度 [℃]。
        heat_exchangers (list[HeatExchanger]): 熱交換器のリスト。
        external_heating_demand (float): 必要加熱量[W]。
        external_cooling_demand (float): 必要冷却熱量[W]。

    Raises:
        ValueError: 流体のidが重複している場合。また、最小接近温度差の値が不正な場合。
        RuntimeError: 受熱流体、与熱流体が一つも指定されていない場合。
    """

    def __init__(
        self,
        streams_: list[Stream],
        minimum_approach_temp_diff: float,
        force_validation: bool = False
    ):
        streams = deepcopy(streams_)

        id_set: set[str] = set()
        for stream in streams:
            if stream.id_ in id_set:
                raise ValueError(
                    '流体のidは一意である必要があります。'
                    f'重複しているid: {stream.id_}'
                )
            id_set.add(stream.id_)

        if not is_valid_streams(streams):
            raise ValueError('与熱流体および受熱流体は少なくとも1つは指定する必要があります。')

        # 外部流体が存在する場合は検証を行う。
        ignore_validation = True
        for stream in streams:
            if stream.is_external():
                ignore_validation = False
                break

        if force_validation:
            ignore_validation = False

        self.minimum_approach_temp_diff_range = get_possible_minimum_temp_diff_range(
            streams,
            ignore_validation
        )

        if minimum_approach_temp_diff not in self.minimum_approach_temp_diff_range:
            raise ValueError(
                "最小接近温度差が不正です。"
                f"指定最小接近温度差 [℃]: {minimum_approach_temp_diff}, "
                f"設定可能最小接近温度差 [℃]: {self.minimum_approach_temp_diff_range.start:.3f}"
                f" ~ {self.minimum_approach_temp_diff_range.finish:.3f}"
            )

        self.gcc = GrandCompositeCurve(streams, minimum_approach_temp_diff)
        self.external_heating_demand = self.gcc.heats[-1]
        self.external_cooling_demand = self.gcc.heats[0]

        id_heats = self.gcc.solve_external_heat()
        for stream in streams:
            for id_, heat in id_heats.items():
                if stream.id_ == id_:
                    stream.update_heat(heat)

        self.streams = [stream for stream in streams if stream.heat() != 0]
        self.pinch_point_temp = self.gcc.pinch_point_temp()
        self.tq = TQDiagram(
            self.streams,
            minimum_approach_temp_diff,
            self.pinch_point_temp
        )

        all_heat_ranges = get_merged_heat_ranges(
            [
                [plot_segment.heat_range for plot_segment in self.tq.hcc_merged],
                [plot_segment.heat_range for plot_segment in self.tq.ccc_merged]
            ]
        )
        hot_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
            s.heat_range: s for s in get_plot_segments(all_heat_ranges, self.tq.hcc_merged)
        }
        cold_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
            s.heat_range: s for s in get_plot_segments(all_heat_ranges, self.tq.ccc_merged)
        }

        self.heat_exchangers: list[HeatExchanger] = []
        for heat_range in all_heat_ranges:
            hot_plot_segment = hot_heat_range_plot_segment.get(heat_range, None)
            cold_plot_segment = cold_heat_range_plot_segment.get(heat_range, None)

            if hot_plot_segment is None or cold_plot_segment is None:
                continue

            self.heat_exchangers.append(
                HeatExchanger(heat_range, hot_plot_segment, cold_plot_segment)
            )

    def create_grand_composite_curve(self) -> tuple[list[float], list[float]]:
        """グランドコンポジットカーブを描くために必要な熱量と温度を返します。
        """
        return self.gcc.heats, self.gcc.temps

    def create_tq(self) -> tuple[list[Line], list[Line]]:
        """tq線図をを描くために必要な与熱複合線および受熱複合線を返します。
        """
        return (
            self.tq.hot_lines,
            self.tq.cold_lines
        )

    def create_tq_separated(self) -> tuple[list[Line], list[Line]]:
        """流体ごとに分割したtq線図をを描くために必要な与熱複合線および受熱複合線を返します。
        """
        return (
            self.tq.hot_lines_separated,
            self.tq.cold_lines_separated
        )

    def create_tq_split(self) -> tuple[list[Line], list[Line]]:
        """流体ごとに分割し、最小接近温度差の条件を満たしたtq線図をを描くために必要な与熱複合線および受熱複合線を返します。
        """
        return (
            self.tq.hot_lines_split,
            self.tq.cold_lines_split
        )

    def create_tq_merged(self) -> tuple[list[Line], list[Line]]:
        """結合可能な熱交換器を結合したtq線図をを描くために必要な与熱複合線および受熱複合線を返します。
        """
        return (
            self.tq.hot_lines_merged,
            self.tq.cold_lines_merged
        )

    def get_heat_exchanger_cost(self, ignore_unknown: bool = True) -> float:
        return sum(
            calculate_heat_exchanger_cost(
                heat_exchanger.get_area(ignore_unknown),
                heat_exchanger.reboiler_or_reactor
            ) for heat_exchanger in self.heat_exchangers
        )
