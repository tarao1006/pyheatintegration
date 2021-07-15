Step4. Export to Excel
======================

.. note::
  Matplotlibではなく、Excelを用いてグラフを作成したい方向けの説明です。

グラフを作成する際にmatplotlibではなくExcelを用いたい場合、プロットに必要なデータを加工する必\
要があります。例で用いる ``analyzer`` は以下のコードによって作成されたと仮定しています。

.. code-block:: python

  from pyheatintegration import PinchAnalyzer, Stream

  streams = [
      Stream(40.0, 90.0, 150.0),
      Stream(80.0, 110.0, 180.0),
      Stream(125.0, 80.0, 180.0),
      Stream(100.0, 60.0, 160.0)
  ]

  minimum_approach_temperature_difference = 10.0
  analyzer = PinchAnalyzer(streams, minimum_approach_temperature_difference)

``convert_to_excel_data`` を用いることで、直線のリストをx座標のリストとy座標のリストに変換\
することができます。その後、例えば ``numpy`` などを用いてCSVファイルに書き込んだ後に、Excel\
で処理してください。

.. code-block:: python

  from pyheatintegration import convert_to_excel_data
  import numpy as np

  hot_lines, cold_lines = analyzer.create_tq()
  hot_lines_excel = convert_to_excel_data(hot_lines)
  cold_lines_excel = convert_to_excel_data(cold_lines)

  print(hot_lines_excel)
  # ([0.0, 40.0, 80.0, 160.0, 240.0, 250.0, 340.0], [60.0, 70.0, 80.0, 90.0, 100.0, 102.5, 125.0])

  print(cold_lines_excel)
  # ([40.0, 80.0, 160.0, 240.0, 250.0, 340.0, 370.0], [40.0, 53.33333333333333, 80.0, 88.88888888888889, 90.0, 105.0, 110.0])

  np.savetxt("./tq_diagram_hot.csv", np.array(hot_lines_excel).T)
  np.savetxt("./tq_diagram_cold.csv", np.array(cold_lines_excel).T)
