from collections import UserList
from copy import deepcopy
from typing import Optional, cast

from .heat_range import REL_TOL_DIGIT, HeatRange, get_heat_ranges, get_heats
from .line import Line
from .plot_segment import PlotSegment, get_plot_segments, temp_diff
from .stream import Stream
from .temperature_range import TemperatureRange


class Segment:
    heat_range: HeatRange
    heat_ranges: list[HeatRange]
    hot_temperature_range: Optional[TemperatureRange]
    cold_temmperature_range: Optional[TemperatureRange]
    hot_streams: list[Stream]
    cold_streams: list[Stream]

    hot_plot_segments: list[PlotSegment]
    cold_plot_segments: list[PlotSegment]
    hot_plot_segments_separated: list[PlotSegment]
    cold_plot_segments_separated: list[PlotSegment]
    hot_plot_segments_splitted: list[PlotSegment]
    cold_plot_segments_splitted: list[PlotSegment]

    def __init__(
        self,
        heats: tuple[float, float],
        hot_temperatures: Optional[tuple[float, float]] = None,
        cold_temperatures: Optional[tuple[float, float]] = None,
        hot_streams_: list[Stream] = [],
        cold_streams_: list[Stream] = []
    ):
        self.heat_range = HeatRange(*heats)

        self.hot_streams = deepcopy(hot_streams_)
        self.hot_temperature_range = None
        self.hot_plot_segments = []
        self.hot_plot_segments_separated_streams = []
        if hot_temperatures is not None:
            self.hot_temperature_range = TemperatureRange(*hot_temperatures)
            self.hot_plot_segments.append(PlotSegment(
                *self.heat_range(),
                *self.hot_temperature_range()
            ))
            self.hot_plot_segments_separated_streams = self.init_plot_segments_separated_streams(
                self.hot_streams,
                self.hot_temperature_range
            )

        self.cold_streams = deepcopy(cold_streams_)
        self.cold_temperature_range = None
        self.cold_plot_segments = []
        self.cold_plot_segments_separated_streams = []
        if cold_temperatures is not None:
            self.cold_temperature_range = TemperatureRange(*cold_temperatures)
            self.cold_plot_segments.append(PlotSegment(
                *self.heat_range(),
                *self.cold_temperature_range()
            ))
            self.cold_plot_segments_separated_streams = self.init_plot_segments_separated_streams(
                self.cold_streams,
                self.cold_temperature_range
            )

        hot_heats = get_heats([
            plot_segment.heat_range
            for plot_segment in self.hot_plot_segments_separated_streams
        ])
        cold_heats = get_heats([
            plot_segment.heat_range
            for plot_segment in self.cold_plot_segments_separated_streams
        ])

        # 与熱流体と受熱流体を合わせた熱量変化帯を得る。
        self.heat_ranges = get_heat_ranges(sorted(list(set(hot_heats + cold_heats))))

        self.hot_plot_segments_separated = get_plot_segments(
            self.heat_ranges,
            self.hot_plot_segments_separated_streams
        )
        self.cold_plot_segments_separated = get_plot_segments(
            self.heat_ranges,
            self.cold_plot_segments_separated_streams
        )

    def __repr__(self) -> str:
        return (
            "Segment("
            f"{self.heat_range.start}, "
            f"{self.heat_range.finish}, "
            f"{self.hot_temperature_range}, "
            f"{self.cold_temperature_range})"
        )

    def __str__(self) -> str:
        return (
            f"({self.heat_range.start}, {self.heat_range.finish})"
            f"({self.hot_temperature_range})"
            f"({self.cold_temperature_range})"
            f"{self.hot_streams}"
            f"{self.cold_streams}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Segment):
            return NotImplemented
        return self.heat_range() == other.heat_range()

    @classmethod
    def round(self, x: float) -> float:
        return round(x, REL_TOL_DIGIT)

    def init_plot_segments_separated_streams(
        self,
        streams: list[Stream],
        temperature_range: TemperatureRange
    ) -> list[PlotSegment]:
        res: list[PlotSegment] = []
        start_heat = self.heat_range.start
        for i in range(len(streams)):
            heat = streams[i].heat()
            start_heat = self.round(start_heat)
            if i == len(streams) - 1:
                finish_heat = self.round(self.heat_range.finish)
            else:
                finish_heat = self.round(start_heat + heat)
            res.append(PlotSegment(
                start_heat,
                finish_heat,
                *temperature_range(),
                str(streams[i].id_)
            ))
            start_heat += heat
        return res

    def split(self, minimum_approach_temp_diff: float) -> None:
        """最小接近温度差を満たすように熱交換器を分割する。
        """
        minimum_temp_diff = minimum_approach_temp_diff

        hot_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
            plot_segment.heat_range: plot_segment
            for plot_segment in self.hot_plot_segments_separated
        }

        cold_heat_range_plot_segment: dict[HeatRange, PlotSegment] = {
            plot_segment.heat_range: plot_segment
            for plot_segment in self.cold_plot_segments_separated
        }

        for heat_range in self.heat_ranges:
            hot_plot_segment = hot_heat_range_plot_segment.get(heat_range, None)
            cold_plot_segment = cold_heat_range_plot_segment.get(heat_range, None)

            self.hot_temperature_range = cast(
                TemperatureRange,
                self.hot_temperature_range
            )
            self.cold_temperature_range = cast(
                TemperatureRange,
                self.cold_temperature_range
            )

            if hot_plot_segment is None or cold_plot_segment is None:
                continue

            start_temp_diff, finish_temp_diff = temp_diff(
                hot_plot_segment,
                cold_plot_segment
            )

            if start_temp_diff < minimum_temp_diff or finish_temp_diff < minimum_temp_diff:
                hot_heat_range_plot_segment[heat_range] = PlotSegment(
                    *heat_range(),
                    *self.hot_temperature_range(),
                    hot_plot_segment.uuid
                )
                cold_heat_range_plot_segment[heat_range] = PlotSegment(
                    *heat_range(),
                    *self.cold_temperature_range(),
                    cold_plot_segment.uuid
                )

                for heat_range_ in self.heat_ranges:
                    if heat_range == heat_range_:
                        continue

                    hot_plot_segment_ = hot_heat_range_plot_segment.get(
                        heat_range_,
                        None
                    )
                    cold_plot_segment_ = cold_heat_range_plot_segment.get(
                        heat_range_,
                        None
                    )
                    if hot_plot_segment_ is not None and hot_plot_segment_.uuid == hot_plot_segment.uuid:
                        hot_heat_range_plot_segment[heat_range_] = PlotSegment(
                            *heat_range_(),
                            *self.hot_temperature_range(),
                            hot_plot_segment.uuid
                        )

                    if cold_plot_segment_ is not None and cold_plot_segment_.uuid == cold_plot_segment.uuid:
                        cold_heat_range_plot_segment[heat_range_] = PlotSegment(
                            *heat_range_(),
                            *self.cold_temperature_range(),
                            cold_plot_segment.uuid
                        )

        self.hot_plot_segments_splitted = sorted(list(hot_heat_range_plot_segment.values()))
        self.cold_plot_segments_splitted = sorted(list(cold_heat_range_plot_segment.values()))


class Segments(UserList[Segment]):

    def get_lines(
        self,
        plot_segments: list[PlotSegment]
    ) -> list[Line]:
        return [plot_segment.line() for plot_segment in plot_segments]

    def hot_lines(self) -> list[Line]:
        return [line for segment in self.data for line in self.get_lines(segment.hot_plot_segments)]

    def cold_lines(self) -> list[Line]:
        return [line for segment in self.data for line in self.get_lines(segment.cold_plot_segments)]

    def hot_lines_separated(self) -> list[Line]:
        return [line for segment in self.data for line in self.get_lines(segment.hot_plot_segments_separated)]

    def cold_lines_separated(self) -> list[Line]:
        return [line for segment in self.data for line in self.get_lines(segment.cold_plot_segments_separated)]

    def hot_lines_splitted(self) -> list[Line]:
        return [line for segment in self.data for line in self.get_lines(segment.hot_plot_segments_splitted)]

    def cold_lines_splitted(self) -> list[Line]:
        return [line for segment in self.data for line in self.get_lines(segment.cold_plot_segments_splitted)]

    def split(self, minimum_approach_temp_diff: float) -> None:
        for segment in self.data:
            segment.split(minimum_approach_temp_diff)
