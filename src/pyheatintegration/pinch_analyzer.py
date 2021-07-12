from copy import deepcopy

from .grand_composite_curve import GrandCompositeCurve
from .line import Line
from .stream import Stream
from .tq_diagram import TQDiagram, get_possible_minimum_temp_diff_range


class PinchAnalyzer:
    """エントリーポイント。
    """

    def __init__(
        self,
        streams_: list[Stream],
        minimum_approach_temp_diff: float
    ):
        streams = deepcopy(streams_)

        id_set: set[str] = set()
        for stream in streams:
            if stream.id_ in id_set:
                raise ValueError('流体のidは一意である必要があります。')
            id_set.add(stream.id_)

        hot_streams = sorted(
            [stream for stream in streams if stream.is_hot()],
            key=lambda s: s.output_temperature()
        )
        cold_streams = sorted(
            [stream for stream in streams if stream.is_cold()],
            key=lambda s: s.input_temperature()
        )

        if not hot_streams:
            raise RuntimeError('与熱流体は少なくとも1つは指定する必要があります。')
        if not cold_streams:
            raise RuntimeError('受熱流体は少なくとも1つは指定する必要があります。')

        minimum_approach_temp_diff_range = get_possible_minimum_temp_diff_range(streams)

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
