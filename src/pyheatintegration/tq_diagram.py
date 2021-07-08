import math
from copy import copy, deepcopy
from typing import Callable, Optional

from .heat_exchanger import HeatExchanger
from .heat_range import (REL_TOL_DIGIT, HeatRange, get_detailed_heat_ranges,
                         get_heat_ranges, get_heats)
from .plot_segment import PlotSegment, get_plot_segments, is_continuous
from .segment import Segment, Segments
from .stream import Stream, get_temperature_range_heats
from .temperature_range import accumulate_heats, get_temperatures


def _create_composite_curve(streams: list[Stream]) -> list[PlotSegment]:
    """受け取った流体から生成した複合線を返します。

    Args:
        streams (list[Stream]): 流体のリスト。

    Returns:
        list[PlotSegment]: 複合線。
    """
    t_ranges, t_range_heats = get_temperature_range_heats(streams)
    t = get_temperatures(t_ranges)
    h = accumulate_heats(t_ranges, t_range_heats)
    return [
        PlotSegment(h[i], h[i + 1], t[i], t[i + 1]) for i in range(len(h) - 1)
    ]


def _get_heat_at_pinch_point(
    plot_segments: list[PlotSegment],
    pinch_point_temp: float,
    get_temp: Callable[[PlotSegment], float]
) -> float:
    """ピンチポイントとなる温度での熱量を返します。

    Args:
        plot_segment (list[PlotSegment]): 複合線。プロットセグメントのリスト。
        pinch_point_temp (float): ピンチポイントとなる温度[℃]。
        get_temp (Callable[[PlotSegment], float]):
            温度変化がないプロットセグメントがピンチポイントを取る場合に返す熱量。

    Returns:
        float: ピンチポイントでの熱量[W]。

    Raises:
        RuntimeError: 複合線がピンチポイントとなる温度を取らない場合。
    """
    for plot_segment in plot_segments:
        if plot_segment.contain_temperature(pinch_point_temp):
            # 熱量変化がない場合は無視する。隣接するプロットセグメントが同じ温度を取るので、
            # そのプロットセグメントの情報を利用する。
            if plot_segment.heat_range.delta == 0:
                continue

            # 与熱流体の場合、温度変化がないプロットセグメントは、右側がピンチポイントとなる。
            # 受熱流体の場合、温度変化がないプロットセグメントは、左側がピンチポイントとなる。
            if plot_segment.temperature_range.delta == 0:
                return get_temp(plot_segment)
            else:
                return plot_segment.heat_at_temperature(pinch_point_temp)

    raise RuntimeError('複合線がピンチポイントとなる温度を取りません。')


def _shift_curve(
    hot_plot_segments_: list[PlotSegment],
    cold_plot_segments_: list[PlotSegment],
    minimum_approach_temp_diff: float,
    pinch_point_temp: float
) -> tuple[list[PlotSegment], list[PlotSegment]]:
    """ピンチポイントが最小接近誤差となるように受熱複合線と与熱複合線をずらします。

    ピンチポイントは、与熱流体の場合は下に凸な箇所、受熱流体の場合は上に凸な箇所です。

    Args:
        hot_plot_segments_ (list[PlotSegment]): 与熱複合線。
        cold_plot_segments_ (list[PlotSegment]): 受熱複合線。
        minimum_approach_temp_diff (float): 最小接近温度差[℃]。
        pinch_point_temp (float): ピンチポイントの温度[℃]。

    Returns:
        tuple[list[PlotSegment], list[PlotSegment]]:
            最小接近温度差を満たす与熱複合線と受熱複合線。

    Raises:
        ValueError: 複合線が熱量に関して連続でない場合。
    """
    hot_plot_segments = sorted(deepcopy(hot_plot_segments_))
    cold_plot_segments = sorted(deepcopy(cold_plot_segments_))

    if is_continuous(hot_plot_segments) is not None \
       or is_continuous(cold_plot_segments) is not None:
        raise ValueError(
            '不正な複合線です。'
            '複合線は熱量に関して連続である必要があります。'
        )

    hot_heat_at_pinch_point = _get_heat_at_pinch_point(
        hot_plot_segments,
        pinch_point_temp,
        lambda x: x.finish_heat()
    )

    cold_heat_at_pinch_point = _get_heat_at_pinch_point(
        cold_plot_segments,
        pinch_point_temp - minimum_approach_temp_diff,
        lambda x: x.start_heat()
    )

    gap = round(
        hot_heat_at_pinch_point - cold_heat_at_pinch_point, REL_TOL_DIGIT
    )

    for plot_segment in cold_plot_segments:
        plot_segment.shift_heat(gap)

    return hot_plot_segments, cold_plot_segments


def _get_segments(
    hot_plot_segments: list[PlotSegment],
    cold_plot_segments: list[PlotSegment],
    hot_streams: list[Stream],
    cold_streams: list[Stream]
) -> Segments:
    """プロットセグメントの情報から得たセグメントを返します。

    Args:
        hot_plot_segments (list[PlotSegment]): 与熱複合線。
        cold_plot_segments (list[PlotSegment]): 受熱複合線。
        hot_streams (list[Stream]): 与熱流体。
        cold_streams (list[Stream]): 受熱流体。

    Returns:
        Segments: セグメントのリスト。
    """
    heat_ranges = get_detailed_heat_ranges(
        [
            [plot_segment.heat_range for plot_segment in hot_plot_segments],
            [plot_segment.heat_range for plot_segment in cold_plot_segments]
        ]
    )

    hot_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
        s.heat_range: s for s in get_plot_segments(heat_ranges, hot_plot_segments)
    }
    cold_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
        s.heat_range: s for s in get_plot_segments(heat_ranges, cold_plot_segments)
    }

    segments: Segments = Segments()
    for heat_range in heat_ranges:
        hot_plot_segment = hot_heat_range_plot_segment.get(heat_range, None)
        hot_temperatures: Optional[tuple[float, float]] = None
        hot_streams_: list[Stream] = []
        if hot_plot_segment is not None:
            hot_temp_range = hot_plot_segment.temperature_range
            hot_temperatures = hot_temp_range()

            for stream_ in hot_streams:
                if stream_.contain_temperatures(hot_temperatures):
                    stream = copy(stream_)
                    if hot_temp_range.delta == 0:
                        if stream.is_isothermal():
                            stream.update_heat(heat_range.delta)
                        else:
                            continue
                    else:
                        if stream.is_isothermal():
                            continue
                        else:
                            stream.update_temperature(*hot_temperatures)
                    hot_streams_.append(stream)

        cold_plot_segment = cold_heat_range_plot_segment.get(heat_range, None)
        cold_temperatures: Optional[tuple[float, float]] = None
        cold_streams_: list[Stream] = []
        if cold_plot_segment is not None:
            cold_temp_range = cold_plot_segment.temperature_range
            cold_temperatures = cold_temp_range()

            for stream_ in cold_streams:
                if stream_.contain_temperatures(cold_temperatures):
                    stream = copy(stream_)

                    if cold_temp_range.delta == 0:
                        if stream.is_isothermal():
                            stream.update_heat(heat_range.delta)
                        else:
                            continue
                    else:
                        if stream.is_isothermal():
                            continue
                        else:
                            stream.update_temperature(*cold_temperatures)
                    cold_streams_.append(stream)

        segments.append(
            Segment(
                heat_range(),
                hot_temperatures,
                cold_temperatures,
                hot_streams_,
                cold_streams_
            )
        )

    return segments


def _merge_segments(
    segments_: Segments
) -> tuple[list[PlotSegment], list[PlotSegment]]:
    """結合可能なセグメントを結合します。

    Args:
        segments_ (Segments): セグメントのリスト。

    Returns:
        tuple[list[PlotSegment], list[PlotSegment]]:
            与熱複合線と受熱複合線。
    """
    segments = deepcopy(segments_)
    hot_plot_segments = sorted([
        plot_segment for segment in segments for plot_segment in segment.hot_plot_segments_splitted
    ])
    cold_plot_segments = sorted([
        plot_segment for segment in segments for plot_segment in segment.cold_plot_segments_splitted
    ])
    heat_ranges = get_heat_ranges(
        get_heats(
            sorted([
                heat_range for segment in segments for heat_range in segment.heat_ranges
            ])
        )
    )
    heat_range_hot_plot_segment = {
        plot_segment.heat_range: plot_segment for plot_segment in hot_plot_segments
    }
    heat_range_cold_plot_segment = {
        plot_segment.heat_range: plot_segment for plot_segment in cold_plot_segments
    }

    merged_heat_ranges: list[HeatRange] = []
    merged_hot_plot_segments: list[PlotSegment] = []
    merged_cold_plot_segments: list[PlotSegment] = []
    for i in range(len(heat_ranges) - 1):
        hot_plot_segment = heat_range_hot_plot_segment.get(heat_ranges[i], None)
        cold_plot_segment = heat_range_cold_plot_segment.get(heat_ranges[i], None)
        next_hot_plot_segment = heat_range_hot_plot_segment.get(heat_ranges[i + 1], None)
        next_cold_plot_segment = heat_range_cold_plot_segment.get(heat_ranges[i + 1], None)

        if hot_plot_segment is None \
           or cold_plot_segment is None \
           or next_hot_plot_segment is None \
           or next_cold_plot_segment is None:
            continue

        if hot_plot_segment.mergiable(next_hot_plot_segment) \
           and cold_plot_segment.mergiable(next_cold_plot_segment):
            merged_heat_range = hot_plot_segment.heat_range.merge(next_hot_plot_segment.heat_range)
            merged_hot_temp_range = hot_plot_segment.temperature_range.merge(next_hot_plot_segment.temperature_range)
            merged_cold_temp_range = cold_plot_segment.temperature_range.merge(next_cold_plot_segment.temperature_range)
            merged_hot_plot_segments.append(PlotSegment(
                *merged_heat_range(),
                *merged_hot_temp_range(),
                hot_plot_segment.uuid
            ))
            merged_cold_plot_segments.append(PlotSegment(
                *merged_heat_range(),
                *merged_cold_temp_range(),
                cold_plot_segment.uuid
            ))
            merged_heat_ranges.extend([heat_ranges[i], heat_ranges[i + 1]])

    hot_plot_segments = [plot_segment for plot_segment in hot_plot_segments if plot_segment.heat_range not in merged_heat_ranges]
    cold_plot_segments = [plot_segment for plot_segment in cold_plot_segments if plot_segment.heat_range not in merged_heat_ranges]

    hot_plot_segments.extend(merged_hot_plot_segments)
    cold_plot_segments.extend(merged_cold_plot_segments)

    return sorted(hot_plot_segments), sorted(cold_plot_segments)


def get_possible_minimum_temp_diff(
    streams: list[Stream]
) -> float:
    """設定可能な最小接近温度差を返します。

    Args:
        streams (list[Stream]): 流体のリスト。

    Returns:
        float: 可能な最小接近温度差[℃]。
    """
    cold_streams = sorted(
        [stream for stream in streams if stream.is_internal() and stream.is_cold()],
        key=lambda stream: stream.input_temperature()
    )
    hot_streams = sorted(
        [stream for stream in streams if stream.is_internal() and stream.is_hot()],
        key=lambda stream: stream.output_temperature()
    )

    if not hot_streams:
        raise RuntimeError('与熱流体は少なくとも1つは指定する必要があります。')
    if not cold_streams:
        raise RuntimeError('受熱流体は少なくとも1つは指定する必要があります。')

    # 与熱流体と受熱流体のセグメントを得る。
    initial_hcc = _create_composite_curve(hot_streams)
    initial_ccc = _create_composite_curve(cold_streams)

    initial_heat_ranges = get_detailed_heat_ranges(
        [
            [plot_segment.heat_range for plot_segment in initial_hcc],
            [plot_segment.heat_range for plot_segment in initial_ccc]
        ]
    )

    hcc = get_plot_segments(initial_heat_ranges, initial_hcc)
    ccc = get_plot_segments(initial_heat_ranges, initial_ccc)

    hot_maximum_heat = max(s.finish_heat() for s in hcc)
    cold_maximum_heat = max(s.finish_heat() for s in ccc)

    # 与熱複合線の方が大きい場合、複合線は右で揃える。
    # 受熱複合線の方が大きい場合、複合線は左で揃える。
    if hot_maximum_heat >= cold_maximum_heat:
        gap = hot_maximum_heat - cold_maximum_heat
        for plot_segment in ccc:
            plot_segment.shift_heat(gap)

    # ずらした複合線の与熱流体と受熱流体を合わせた熱量領域を得る。
    heat_ranges = get_detailed_heat_ranges(
        [
            [plot_segment.heat_range for plot_segment in hcc],
            [plot_segment.heat_range for plot_segment in ccc]
        ]
    )

    # 与熱流体と受熱流体を合わせた熱量領域に対応するセグメントを得る。
    hot_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
        plot_segment.heat_range: plot_segment
        for plot_segment in get_plot_segments(heat_ranges, hcc)
    }
    cold_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
        plot_segment.heat_range: plot_segment
        for plot_segment in get_plot_segments(heat_ranges, ccc)
    }

    min_temp_diff = math.inf
    for heat_range in heat_ranges:
        hot_plot_segment = hot_heat_range_plot_segment.get(heat_range, None)
        cold_plot_segment = cold_heat_range_plot_segment.get(heat_range, None)

        if hot_plot_segment is None or cold_plot_segment is None:
            continue

        hot_start_temp, hot_finish_temp = hot_plot_segment.temperatures()
        cold_start_temp, cold_finish_temp = cold_plot_segment.temperatures()

        min_temp_diff = min(
            min_temp_diff,
            hot_start_temp - cold_start_temp,
            hot_finish_temp - cold_finish_temp
        )

    return min_temp_diff


class TQDiagram:
    """TQ線図を描くために必要な情報を得るためのクラス。

    Args:
        streams (list[Stream]): 熱交換を行いたい流体。
        minimum_approach_temp_diff (float): 最小接近温度差[℃]。
        pinch_point_temp (float): ピンチポイントの温度[℃]。

    Attributes:
        heat_exchangers (list[HeatExchanger]): 熱交換器のリスト。
        hot_lines (list[Line]): TQ線図の与熱複合線。
        cold_linse (list[Line]): TQ線図の受熱複合線。
        hot_lines_separated (list[Line]): 流体ごとに分割した与熱複合線。
        cold_lines_separated (list[Line]): 流体ごとに分割した受熱複合線。
        hot_lines_splitted (list[Line]): 流体ごとに分割し、最小接近温度差を満たした与熱複合線。
        cold_lines_splitted (list[Line]): 流体ごとに分割し、最小接近温度差を満たした受熱複合線。
        hot_lines_merged (list[Line]): 熱交換器を結合した与熱複合線。
        cold_lines_merged (list[Line]): 熱交換器を結合した受熱複合線。
    """

    def __init__(
        self,
        streams: list[Stream],
        minimum_approach_temp_diff: float,
        pinch_point_temp: float
    ):
        hot_streams = sorted(
            [stream for stream in streams if stream.is_hot()],
            key=lambda stream: stream.output_temperature()
        )

        cold_streams = sorted(
            [stream for stream in streams if stream.is_cold()],
            key=lambda stream: stream.input_temperature()
        )

        # 与熱複合線と受熱複合線を得た後に、最小接近温度差を満たすようにずらす。
        hcc, ccc = _shift_curve(
            _create_composite_curve(hot_streams),
            _create_composite_curve(cold_streams),
            minimum_approach_temp_diff,
            pinch_point_temp
        )

        # セグメントを得る。
        segments = _get_segments(hcc, ccc, hot_streams, cold_streams)

        # 最小接近温度差を満たすように分割を行う
        segments.split(minimum_approach_temp_diff)

        self.hot_lines = segments.hot_lines()
        self.cold_lines = segments.cold_lines()

        self.hot_lines_separated = segments.hot_lines_separated()
        self.cold_lines_separated = segments.cold_lines_separated()

        self.hot_lines_splitted = segments.hot_lines_splitted()
        self.cold_lines_splitted = segments.cold_lines_splitted()

        # 結合可能なセグメント同士を結合する。
        hcc_merged, ccc_merged = _merge_segments(segments)
        self.hot_lines_merged = [plot_segment.line() for plot_segment in hcc_merged]
        self.cold_lines_merged = [plot_segment.line() for plot_segment in ccc_merged]

        all_heat_ranges = get_detailed_heat_ranges(
            [
                [plot_segment.heat_range for plot_segment in hcc_merged],
                [plot_segment.heat_range for plot_segment in ccc_merged]
            ]
        )
        hot_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
            s.heat_range: s for s in get_plot_segments(all_heat_ranges, hcc_merged)
        }
        cold_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
            s.heat_range: s for s in get_plot_segments(all_heat_ranges, ccc_merged)
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
