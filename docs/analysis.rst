Step2. Analysis
===============

.. note::
  流体の指定方法をまた読んでいない方は、 まずは :doc:`create_stream` を読んでください。

流体を生成した後、 ``PinchAnalyzer`` を用いてグランドコンポジットカーブおよびTQ線図を書きま\
す。 ``PinchAnalyzer`` のコンストラクタは以下のようになっています。

.. py:class:: PinchAnalyzer(streams_: list[Stream], minimum_approach_temp_diff: float, ignore_maximum: bool = False)

* ``streams_ (list[Stream])``: 流体のリスト。
* ``minimum_approach_temp_diff (float)``: 最小接近温度差 [℃]。
* ``ignore_maximum (bool, optional)``: 最小接近温度差を指定可能かを検証する際に、最大値
  のチェックを無視するかどうか。

.. note::
  外部流体を指定せずに解析を行いたい場合などに ``ignore_maximum`` を指定すると、エラーが生じ\
  ずに解析を行うことが可能となる可能性があります。

**例**

.. code-block:: python

  streams = [
      Stream(40.0, 90.0, 150.0, StreamType(1), StreamState.LIQUID, 0.0, False, 'cold1')
      Stream(80.0, 110.0, 180.0, StreamType(1), StreamState.LIQUID, 0.0, False, 'cold2')
      Stream(125.0, 80.0, 180.0, StreamType(2), StreamState.GAS, 0.0, False, 'hot1')
      Stream(100.0, 60.0, 160.0, StreamType(2), StreamState.GAS, 0.0, False, 'hot2')
      Stream(20.0, 20.0, 0.0, StreamType(3), StreamState.LIQUID_EVAPORATION, 100.0, False, 'external cold1')
      Stream(150.0, 150.0, 0.0, StreamType(4), StreamState.GAS_CONDENSATION, 200.0, False, 'external hot1')
  ]

  analyzer = PinchAnalyzer(streams, 10.0)

流体の検証
-----------------------

コンストラクタで受け取った流体のリストのバリデーションを行います。以下の場合に不正と判断します。\
ただし、 ``ignore_maximum`` を ``True`` とした場合、3の条件は無視されます。

1. 流体のidが重複している場合
2. 与熱流体もしくは受熱流体が1つもない場合
3. ``与熱流体の最高温度 < 受熱流体の最高温度`` または ``与熱流体の最低温度 > 受熱流体の最低温度`` である場合

最小接近温度差の検証
-----------------------

最小接近温度差は、指定可能範囲が存在する。指定値がその範囲にない場合、不正と判断します。指定可能\
な最大値を、 ``min(与熱流体の最高温度 - 受熱流体の最高温度, 与熱流体の最低温度 - 受熱流体の最低温度)``\
とします。ただし、``ignore_maximum`` を ``True`` とした場合には、指定可能な最大値を
``与熱流体の最高温度 - 受熱流体の最低温度`` とします。


グラフ描画
-----------------------

``PinchAnalyzer`` のインスタンス生成時に、グランドコンポジットカーブおよびTQ線図の描画に必要\
な計算が行われます。計算した結果は以下の ``create_*`` を呼ぶことで得ることができます。実際の\
グラフ描画については :doc:`draw_graph` を参照して下さい。

* ``create_grand_composite_curve``: グランドコンポジットカーブ
* ``create_tq``: TQ線図
* ``create_tq_separated``: 流体ごとに分割したTQ線図
* ``create_tq_splitted``: 流体ごとに分割し、最初接近温度差を満たすように分割したTQ線図
* ``create_tq_merged``: 結合可能な熱交換器を結合したTQ線図
