Draw Diagram
============

.. code-block:: python

   import matplotlib.pyplot as plt
   from matplotlib.collections import LineCollection

   from src.pyheatintegration import (PinchAnalyzer, Stream, StreamType,
                                      extract_x, y_range)

   # 熱交換を行う流体を準備
   streams = [
      Stream(40.0, 90.0, 150.0, StreamType(1), 'cold1'),
      Stream(80.0, 110.0, 180.0, StreamType(1), 'cold2'),
      Stream(125.0, 80.0, 180.0, StreamType(2), 'hot1'),
      Stream(100.0, 60.0, 160.0, StreamType(2), 'hot2')
   ]
   minimum_approach_temperature_difference = 10.0
   analyzer = PinchAnalyzer(streams, minimum_approach_temperature_difference)

   # グランドコンポジットカーブ
   heats, temps = analyzer.create_grand_composite_curve()
   fig, ax = plt.subplots(1, 1)
   ax.set_xlabel("Q [kW]")
   ax.set_ylabel("Shifted Temperature [℃]")
   ax.plot(heats, temps)
   fig.savefig("path/to/grand_composite_curve.png")

   # TQ線図
   hot_lines, cold_lines = analyzer.create_tq()
   ymin, ymax = y_range(hot_lines + cold_lines)
   heats = extract_x(hot_lines + cold_lines)
   fig, ax = plt.subplots(1, 1)
   ax.set_xlabel("Q [kW]")
   ax.set_ylabel("T [℃]")
   ax.add_collection(LineCollection(hot_lines, colors="#ff7f0e"))
   ax.add_collection(LineCollection(cold_lines, colors="#1f77b4"))
   ax.vlines(heats, ymin=ymin, ymax=ymax, linestyles=':', colors='k')
   ax.autoscale()
   fig.savefig("path/to/tq_diagram.png")

   # 分割したTQ線図
   hot_lines_separated, cold_lines_separated = analyzer.create_tq_separated()
   ymin, ymax = y_range(hot_lines_separated + cold_lines_separated)
   heats_separated = extract_x(hot_lines_separated + cold_lines_separated)
   fig, ax = plt.subplots(1, 1)
   ax.set_xlabel("Q [kW]")
   ax.set_ylabel("T [℃]")
   ax.add_collection(LineCollection(hot_lines_separated, colors="#ff7f0e"))
   ax.add_collection(LineCollection(cold_lines_separated, colors="#1f77b4"))
   ax.vlines(heats_separated, ymin=ymin, ymax=ymax, linestyles=':', colors='gray')
   ax.vlines(heats, ymin=ymin, ymax=ymax, linestyles=':', colors='k')
   ax.autoscale()
   fig.savefig("path/to/tq_diagram_separeted.png")

   # 最小接近温度差を満たす分割したTQ線図
   hot_lines_splitted, cold_lines_splitted = analyzer.create_tq_splitted()
   ymin, ymax = y_range(hot_lines_splitted + cold_lines_splitted)
   heats_splitted = extract_x(hot_lines_separated + cold_lines_separated)
   fig, ax = plt.subplots(1, 1)
   ax.set_xlabel("Q [kW]")
   ax.set_ylabel("T [℃]")
   ax.add_collection(LineCollection(hot_lines_splitted, colors="#ff7f0e"))
   ax.add_collection(LineCollection(cold_lines_splitted, colors="#1f77b4"))
   ax.vlines(heats_splitted, ymin=ymin, ymax=ymax, linestyles=':', colors='gray')
   ax.vlines(heats, ymin=ymin, ymax=ymax, linestyles=':', colors='k')
   ax.autoscale()
   fig.savefig("path/to/tq_diagram_splitted.png")

   # 熱交換器を結合したTQ線図
   hot_lines_merged, cold_lines_merged = analyzer.create_tq_merged()
   ymin, ymax = y_range(hot_lines_merged + cold_lines_merged)
   heats_merged = extract_x(hot_lines_merged + cold_lines_merged)
   fig, ax = plt.subplots(1, 1)
   ax.set_xlabel("Q [kW]")
   ax.set_ylabel("T [℃]")
   ax.add_collection(LineCollection(hot_lines_merged, colors="#ff7f0e"))
   ax.add_collection(LineCollection(cold_lines_merged, colors="#1f77b4"))
   ax.vlines(heats_merged, ymin=ymin, ymax=ymax, linestyles=':', colors='gray')
   ax.autoscale()
   fig.savefig("path/to/tq_diagram_merged.png")
