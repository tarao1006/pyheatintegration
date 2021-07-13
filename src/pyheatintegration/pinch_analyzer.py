from copy import deepcopy
import math

from .grand_composite_curve import GrandCompositeCurve
from .heat_exchanger import HeatExchanger
from .heat_range import HeatRange, get_detailed_heat_ranges
from .line import Line
from .plot_segment import PlotSegment, get_plot_segments
from .stream import Stream
from .tq_diagram import TQDiagram, get_possible_minimum_temp_diff_range


class PinchAnalyzer:
    """エントリーポイント。
    """

    def __init__(
        self,
        streams_: list[Stream],
        minimum_approach_temp_diff: float,
        ignore_maximum: bool = False
    ):
        streams = deepcopy(streams_)

        id_set: set[str] = set()
        for stream in streams:
            if stream.id_ in id_set:
                raise ValueError('流体のidは一意である必要があります。')
            id_set.add(stream.id_)

        hot_streams = sorted(
            [stream for stream in streams if stream.is_hot()],
            key=lambda s: s.sort_key()
        )
        cold_streams = sorted(
            [stream for stream in streams if stream.is_cold()],
            key=lambda s: s.sort_key()
        )

        if not hot_streams:
            raise RuntimeError('与熱流体は少なくとも1つは指定する必要があります。')
        if not cold_streams:
            raise RuntimeError('受熱流体は少なくとも1つは指定する必要があります。')

        minimum_approach_temp_diff_range = get_possible_minimum_temp_diff_range(
            streams,
            ignore_maximum
        )

        if minimum_approach_temp_diff not in minimum_approach_temp_diff_range:
            raise ValueError(
                "最小接近温度差が不正です。"
                f"指定最小接近温度差 [℃]: {minimum_approach_temp_diff}, "
                f"設定可能最小接近温度差 [℃]: {minimum_approach_temp_diff_range.start:.3f}"
                f" - {minimum_approach_temp_diff_range.finish:.3f}"
            )

        self.gcc = GrandCompositeCurve(streams, minimum_approach_temp_diff)
        id_heats = self.gcc.solve_external_heat()
        for stream in streams:
            for id_, heat in id_heats.items():
                if stream.id_ == id_:
                    stream.update_heat(heat)

        self.streams = [stream for stream in streams if stream.heat() != 0]
        self.pinch_point_temp = self.gcc.maximum_pinch_point_temp
        self.tq = TQDiagram(
            self.streams,
            minimum_approach_temp_diff,
            self.pinch_point_temp
        )

        all_heat_ranges = get_detailed_heat_ranges(
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

        self.heat_exchanger_cost = sum(
            self.calculate_heat_exchanger_cost(
                heat_exchanger.area_counterflow,
                heat_exchanger.reboiler_or_reactor
            )
            for heat_exchanger in self.heat_exchangers
        )

    def create_grand_composite_curve(self) -> tuple[list[float], list[float]]:
        """グランドコンポジットカーブを描くために必要な熱量と温度を返します。
        """
        return self.gcc.heats, self.gcc.temps

    def create_tq(self) -> tuple[list[Line], list[Line]]:
        """tq線図をを描くために必要な直線と熱量変化帯を返します。
        """
        return (
            self.tq.hot_lines,
            self.tq.cold_lines
        )

    def create_tq_separated(self) -> tuple[list[Line], list[Line]]:
        """流体ごとに分割したtq線図をを描くために必要な直線と熱量変化帯を返します。
        """
        return (
            self.tq.hot_lines_separated,
            self.tq.cold_lines_separated
        )

    def create_tq_splitted(self) -> tuple[list[Line], list[Line]]:
        """流体ごとに分割し、最小接近温度差の条件を満たしたtq線図をを描くために必要な直線を返します。
        """
        return (
            self.tq.hot_lines_splitted,
            self.tq.cold_lines_splitted
        )

    def create_tq_merged(self) -> tuple[list[Line], list[Line]]:
        """流体ごとに分割し、最小接近温度差の条件を満たしたtq線図をを描くために必要な直線を返します。
        """
        return (
            self.tq.hot_lines_merged,
            self.tq.cold_lines_merged
        )

    def calculate_heat_exchanger_cost(
        self,
        area: HeatExchanger,
        reboiler_or_reactor: bool = False
    ) -> float:
        """熱交換器にかかるコストを返します。

        Args:
            heat_exchanger (HeatExchanger): 熱交換器。
            k (float): 係数。リボイラーまたは反応器の場合は2

        Returns:
            float: コスト[円]。
        """
        if reboiler_or_reactor:
            k = 2.0
        else:
            k = 1.0
        return 1_500_000 * math.pow(area, 0.65) * k
