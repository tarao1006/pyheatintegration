from copy import deepcopy

from .grand_composite_curve import GrandCompositeCurve
from .line import Line
from .stream import Stream
from .tq_diagram import TQDiagram, get_possible_minimum_temp_diff


class PinchAnalyzer:
    """エントリーポイント。
    """

    def __init__(
        self,
        streams_: list[Stream],
        minimum_approach_temp_diff: float
    ):
        hot_streams = sorted(
            [stream for stream in streams_ if stream.is_hot()],
            key=lambda s: s.output_temperature()
        )
        cold_streams = sorted(
            [stream for stream in streams_ if stream.is_cold()],
            key=lambda s: s.input_temperature()
        )

        if not hot_streams:
            raise RuntimeError('与熱流体は少なくとも1つは指定する必要があります。')
        if not cold_streams:
            raise RuntimeError('受熱流体は少なくとも1つは指定する必要があります。')

        streams = hot_streams + cold_streams
        for i, s in enumerate(streams):
            s.set_id(i + 1)

        streams = deepcopy(streams)

        minimum_temp = min(
            stream.input_temperature()
            for stream in streams
            if stream.is_internal() and stream.is_cold()
        )
        maximum_temp = max(
            stream.input_temperature()
            for stream in streams
            if stream.is_internal() and stream.is_hot()
        )

        if minimum_approach_temp_diff < 0:
            raise ValueError(
                f"最小接近温度差に負の値は設定できません。"
                f"最小接近温度差: {minimum_approach_temp_diff}"
            )

        if minimum_temp + minimum_approach_temp_diff > maximum_temp:
            raise ValueError(
                "最小接近温度差が不正です。"
                f"受熱流体最小温度: {minimum_temp} "
                f"与熱流体最大温度: {maximum_temp} "
                f"最小接近温度差: {minimum_approach_temp_diff}"
            )

        if (minimum_temp_diff := get_possible_minimum_temp_diff(streams)) > minimum_approach_temp_diff:
            raise ValueError(
                "最小接近温度差が不正です。"
                f"可能最小接近温度差: {minimum_temp_diff} "
                f"最小接近温度差: {minimum_approach_temp_diff}"
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
