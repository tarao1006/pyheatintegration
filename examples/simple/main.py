import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import LineCollection

from pyheatintegration import (PinchAnalyzer, Stream, StreamState, StreamType,
                               convert_to_excel_data, extract_x, y_range)


def main():
    df = pd.read_csv("./data.csv").fillna({'reboiler_or_reactor': ''})
    streams = [
        Stream(
            row.input_temperature,
            row.output_temperature,
            row.heat_flow,
            StreamType(row.type),
            StreamState(row.state),
            cost=row.cost,
            reboiler_or_reactor=bool(row.reboiler_or_reactor),
            id_=row.id
        ) for _, row in df.iterrows()]

    minimum_approach_temperature_difference = 10.0
    analyzer = PinchAnalyzer(streams, minimum_approach_temperature_difference)

    print(
        f"設定可能最小接近温度差 [℃]: {analyzer.minimum_approach_temp_diff_range.start:.3f}"
        f" ~ {analyzer.minimum_approach_temp_diff_range.finish:.3f}"
    )

    print(f'ピンチポイント [℃]: {analyzer.gcc.pinch_point_temp()}')
    print(f'必要加熱量[W]: {analyzer.external_heating_demand:.3f}')
    print(f'必要冷却量[W]: {analyzer.external_cooling_demand:.3f}')

    for stream in analyzer.streams:
        if stream.is_external() and stream.is_hot():
            print(
                f'外部与熱流体 id: {stream.id_} '
                '\033[1m加熱量\033[0m [W]: '
                f'{stream.heat():.3f} '
                '\033[1mコスト\033[0m [円/s]: '
                f'{stream.heat() * stream.cost:.3f}'
            )

    for stream in analyzer.streams:
        if stream.is_external() and stream.is_cold():
            print(
                f'外部受熱流体 id: {stream.id_} '
                '\033[1m冷却量\033[0m [W]: '
                f'{stream.heat():.3f} '
                '\033[1mコスト\033[0m [円/s]: '
                f'{stream.heat() * stream.cost:.3f}'
            )

    # グランドコンポジットカーブ
    heats, temps = analyzer.create_grand_composite_curve()
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("Shifted Temperature [℃]")
    ax.plot(heats, temps)
    fig.savefig("./grand_composite_curve.png")

    # TQ線図
    hot_lines, cold_lines = analyzer.create_tq()

    # 与熱複合線と受熱複合線
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines, colors="#1f77b4"))
    ax.autoscale()
    fig.savefig("./tq_diagram.png")

    # 熱量の区間ごとのたて線も表示
    ymin, ymax = y_range(hot_lines + cold_lines)
    heats = extract_x(hot_lines + cold_lines)
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines, colors="#1f77b4"))
    ax.vlines(heats, ymin=ymin, ymax=ymax, linestyles=':', colors='k')
    ax.autoscale()
    fig.savefig("./tq_diagram_with_vlines.png")

    # 分割したTQ線図
    hot_lines_separated, cold_lines_separated = analyzer.create_tq_separated()

    # 与熱複合線と受熱複合線
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines_separated, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines_separated, colors="#1f77b4"))
    ax.autoscale()
    fig.savefig("./tq_diagram_separated.png")

    # 熱量の区間ごとのたて線も表示
    ymin, ymax = y_range(hot_lines_separated + cold_lines_separated)
    heats_separated = extract_x(hot_lines_separated + cold_lines_separated)
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines_separated, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines_separated, colors="#1f77b4"))
    ax.vlines(heats_separated, ymin=ymin, ymax=ymax, linestyles=':', colors='gray')
    ax.autoscale()
    fig.savefig("./tq_diagram_separated_with_vlines.png")

    # 最小接近温度差を満たす分割したTQ線図
    hot_lines_split, cold_lines_split = analyzer.create_tq_split()

    # 与熱複合線と受熱複合線
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines_split, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines_split, colors="#1f77b4"))
    ax.autoscale()
    fig.savefig("./tq_diagram_split.png")

    # 熱量の区間ごとのたて線も表示
    ymin, ymax = y_range(hot_lines_split + cold_lines_split)
    heats_split = extract_x(hot_lines_separated + cold_lines_separated)
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines_split, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines_split, colors="#1f77b4"))
    ax.vlines(heats_split, ymin=ymin, ymax=ymax, linestyles=':', colors='gray')
    ax.autoscale()
    fig.savefig("./tq_diagram_split_with_vlines.png")

    # 熱交換器を結合したTQ線図
    hot_lines_merged, cold_lines_merged = analyzer.create_tq_merged()

    # 与熱複合線と受熱複合線
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines_merged, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines_merged, colors="#1f77b4"))
    ax.autoscale()
    fig.savefig("./tq_diagram_merged.png")

    # 熱量の区間ごとのたて線も表示
    ymin, ymax = y_range(hot_lines_merged + cold_lines_merged)
    heats_merged = extract_x(hot_lines_merged + cold_lines_merged)
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.add_collection(LineCollection(hot_lines_merged, colors="#ff7f0e"))
    ax.add_collection(LineCollection(cold_lines_merged, colors="#1f77b4"))
    ax.vlines(heats_merged, ymin=ymin, ymax=ymax, linestyles=':', colors='gray')
    ax.autoscale()
    fig.savefig("./tq_diagram_merged_with_vlines.png")

    # TQ線図(Excel風)
    hot_lines, cold_lines = analyzer.create_tq()
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Q [kW]")
    ax.set_ylabel("T [℃]")
    ax.plot(*convert_to_excel_data(hot_lines), color="#ff7f0e")
    ax.plot(*convert_to_excel_data(cold_lines), color="#1f77b4")
    fig.savefig("./tq_diagram_excel.png")


if __name__ == '__main__':
    main()
