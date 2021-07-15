pyheatintegration reference documentation
=========================================

pyheatintegrationは `プロセス設計`_ で必要なヒートインテグレーションを支援するパッケージで
す。グランドコンポジットカーブの作成、TQ線図の作成、必要な熱交換器数の導出を行うことができます。

Installation
============

::

   pip install pyheatintegration

Examples
========

* `simple example <https://github.com/tarao1006/pyheatintegration/blob/19d6eda58a58e8c4ae0b3e15726297773e0a546c/examples/simple/main.py>`_

Quick Start
===========

.. code-block:: python

   import matplotlib.pyplot as plt
   from matplotlib.collections import LineCollection

   from src.pyheatintegration import PinchAnalyzer, Stream

   # 熱交換を行う流体を準備
   streams = [
      Stream(40.0, 90.0, 150.0),
      Stream(80.0, 110.0, 180.0),
      Stream(125.0, 80.0, 180.0),
      Stream(100.0, 60.0, 160.0)
   ]

   # 最小接近温度差を指定し、作成した流体のリストとともにPinchAnalyzerのインスタンスを得る。
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

* グランドコンポジットカーブ

.. image:: https://raw.githubusercontent.com/tarao1006/pyheatintegration/main/docs/images/grand_composite_curve.png
   :width: 400

* TQ線図

.. image:: https://raw.githubusercontent.com/tarao1006/pyheatintegration/main/docs/images/tq_diagram.png
   :width: 400

より詳しい説明は :doc:`getting_started` を確認してください。

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started

.. toctree::
   :maxdepth: 2
   :caption: API

   pinch_analyzer
   grand_composite_curve
   tq_diagram
   stream
   heat_exchanger
   enums

.. toctree::
   :maxdepth: 2
   :caption: ALL API

   base_range
   errors
   heat_range
   line
   plot_segment
   segment
   temperature_range

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _プロセス設計: http://www.cheme.kyoto-u.ac.jp/processdesign/
