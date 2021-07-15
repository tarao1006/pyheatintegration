Step3. Draw Diagram
===================

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



.. code-block:: python

   streams = [
      Stream(40.0, 90.0, 150.0, StreamType(1), 'cold1'),
      Stream(80.0, 110.0, 180.0, StreamType(1), 'cold2'),
      Stream(125.0, 80.0, 180.0, StreamType(2), 'hot1'),
      Stream(100.0, 60.0, 160.0, StreamType(2), 'hot2')
   ]

``Stream`` のコンストラクタ:


.. code-block:: python

   # 受熱流体の例。StreamType(1)を設定。
   Stream(40.0, 50.0, 150.0, StreamType(1))
   Stream(50.0, 50.0, 150.0, StreamType(1))  # 等温

   # 与熱流体の例。StreamType(2)を設定。
   Stream(125.0, 80.0, 180.0, StreamType(2))
   Stream(125.0, 125.0, 180.0, StreamType(2))

   # 外部受熱流体の例。StreamType(3)を設定。
   Stream(40.0, 50.0, 0.0, StreamType(3))
   Stream(60.0, 60.0, 0.0, StreamType(3))

   # 外部与熱流体の例。StreamType(4)を設定。
   Stream(125.0, 80.0, 0.0, StreamType(4))
   Stream(100.0, 100.0, 0.0, StreamType(4))

受熱流体は ``入り口温度 ≤ 出口温度`` 、与熱流体は ``入り口温度 ≥ 出口温度`` である必要があります。
等温流体の設定も可能です。外部流体の熱量は、グランドコンポジットカーブ作成時に決定するため、
コンストラクタには ``0`` を渡してください。第五引数にはコストを設定することも可能ですが、現在は
利用していません。将来利用するように変更予定です。

流体のリストと最小接近温度差を引数に ``PinchAnalyzer`` のインスタンスを生成します。

``PinchAnalyzer`` のコンストラクタ:

.. py:class:: PinchAnalyzer(streams: list[Stream], minimum_approach_temperature_difference: float)

.. code-block:: python

   minimum_approach_temperature_difference = 10.0

   # 流体のリストと最小接近温度差を渡してPinchAnalyzerのインスタンスを生成
   analyzer = PinchAnalyzer(streams, minimum_approach_temperature_difference)

   # create_*()を呼ぶことでプロットに必要な情報を取得
   heats, temps = analyzer.create_grand_composite_curve()
   hot_lines, cold_lines = analyzer.create_tq()
   hot_lines_separated, cold_lines_separated = analyzer.create_tq_separated()
   hot_lines_splitted, cold_lines_splitted = analyzer.create_tq_splitted()
   hot_lines_merged, cold_lines_merged = analyzer.create_tq_merged()

``create_tq()`` ``create_tq_separated()`` ``create_tq_splitted()``
``create_tq_merged()`` は、プロットに必要な直線を以下のような形式で返します。

.. code-block:: python

   # [((始点の座標), (終点の座標))...]
   lines = [((0, 0), (1, 1)), ((1, 2), (2, 3))]

タプルの第一成分が直線の始点の座標、第二成分が終点の座標を表します。また、与熱複合線と受熱複合線
をタプルで返します。それぞれを ``matplotlib.collections.LineCollection`` に変換後、
``ax.add_collection`` を行うことで直線をプロットすることができます。

.. code-block:: python

   fig, ax = plt.subplots()
   hot_lines, cold_lines = analyzer.create_tq()
   ax.add_collection(LineCollection(hot_lines))
   ax.add_collection(LineCollection(cold_lines))

複合線において、直線が折れ曲がっている点を通る熱量の線をプロットしたい場合、 ``y_range`` と
``extract_x`` を呼ぶことで、必要な情報を得ることができます。

.. py:function:: y_range(hot_lines: list[Line], cold_lines: list[Line]) -> tuple[float, float]

.. py:function:: extract_x(lines: list[Line]) -> list[float]

.. code-block:: python

   ymin, ymax = y_range(hot_lines + cold_lines)
   heats = extract_x(hot_lines + cold_lines)
   ax.vlines(heats, ymin=ymin, ymax=ymax, linestyles=':', colors='k')