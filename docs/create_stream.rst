Step1. Create Stream
====================

熱交換を行いたい流体の情報を元に、 ``Stream`` のリストを生成します。 ``Stream`` のコンスト\
ラクタは、以下のようになっています。

.. py:class:: Stream(input_temperature: float, output_temperature: float, heat_load: float, type_: StreamType = <StreamType.AUTO: 5>, state: StreamState = <StreamState.UNKNOWN: 5>, cost: float = 0.0, reboiler_or_reactor: bool = False, id_: str = '')

* ``input_temperature (float)``: 入り口温度 [℃]
* ``output_temperature (float)``: 出口温度 [℃]
* ``heat_load (float)``: 熱量 [W]
* ``type_ (StreamType, optional)``: 流体の種類

  * ``StreamType.COLD``: 受熱
  * ``StreamType.HOT``: 与熱
  * ``StreamType.EXTERNAL_COLD``: 外部受熱(冷却用ユーティリティ)
  * ``StreamType.EXTERNAL_HOT``: 外部与熱(加熱用ユーティリティ)
  * ``StreamType.AUTO``: 自動

* ``state (StreamState, optional)``: 流体の状態

  * ``StreamState.GAS``: ガス
  * ``StreamState.LIQUID``: 液
  * ``StreamState.GAS_CONDENSATION``: ガス(凝縮)
  * ``StreamState.LIQUID_EVAPORATION``: 液(蒸発)
  * ``StreamState.UNKNOWN``: 不明/指定しない。

* ``cost (float)``: コスト [円/J] (外部流体の場合)
* ``reboiler_or_reactor (bool, optional)``: リボイラーまたは反応器の熱交換に用いられる\
  か。熱交換器のコストを計算する際の係数を決定するために必要な情報。
* ``id_ (str, optional)``: ID

**例**

.. code-block:: python

  Stream(40.0, 90.0, 150.0, StreamType(1), StreamState.LIQUID, 0.0, False, 'cold1')
  Stream(80.0, 110.0, 180.0, StreamType(1), StreamState.LIQUID, 0.0, False, 'cold2')
  Stream(125.0, 80.0, 180.0, StreamType(2), StreamState.GAS, 0.0, False, 'hot1')
  Stream(100.0, 60.0, 160.0, StreamType(2), StreamState.GAS, 0.0, False, 'hot2')
  Stream(20.0, 20.0, 0.0, StreamType(3), StreamState.LIQUID_EVAPORATION, 100.0, False, 'external cold1')
  Stream(150.0, 150.0, 0.0, StreamType(4), StreamState.GAS_CONDENSATION, 200.0, False, 'external hot1')

入り口温度/出口温度/熱量
------------------------

受熱流体は ``input_temperature ≤ output_temperature`` 、与熱流体は
``input_temperature ≥ output_temperature`` である必要があります。等温流体の設定も可能で\
す。外部流体の熱量は、グランドコンポジットカーブ作成時に決定するため、流体作成時には
``heat_load = 0`` を指定してください。

流体の種類
-----------

流体の種類 ``type_`` は ``enum`` 型である ``StreamType`` を用いて指定します。指定可能な種\
類は、 *受熱* 、*与熱* 、*外部受熱* 、*外部与熱* の4種類です。また、自動で種類を判断するよう\
に指定する *自動* もありますが、明示的に指定する機会はないと思われます。

* ``StreamType.COLD (= 1)``: 受熱
* ``StreamType.HOT (= 2)``: 与熱
* ``StreamType.EXTERNAL_COLD (= 3)``: 外部受熱(冷却用ユーティリティ)
* ``StreamType.EXTERNAL_HOT (= 4)``: 外部与熱(加熱用ユーティリティ)
* ``StreamType.AUTO (= 5)``: 自動

以下の例のように流体を指定します。ただし、オプショナル引数は一部省略しています。

.. code-block:: python

  # 入り口温度: 40 度 出口温度 90 度 熱量 150.0 W の受熱流体
  Stream(40.0, 90.0, 150.0, StreamType(1))

  # 入り口温度: 125 度 出口温度 80 度 熱量 180.0 W の与熱流体
  Stream(125.0, 80.0, 180.0, StreamType(2))

  # 入り口温度: 20 度 出口温度 20 度 の外部受熱流体
  Stream(40.0, 90.0, 0.0, StreamType(3))

  # 入り口温度: 125 度 出口温度 80 度 の外部与熱流体
  Stream(150.0, 150.0, 0.0, StreamType(4))

ただし、外部流体でない場合、入り口温度と出口温度の関係から流体の種類を推測することができるため、\
省略することができます。一方、外部流体は必ず指定する必要があります。

.. code-block:: python

  # 受熱流体と与熱流体はStreamTypeを指定しなくても良い。
  Stream(40.0, 90.0, 150.0)
  Stream(125.0, 80.0, 180.0)

  # 外部受熱流体と外部与熱流体はStreamTypeを指定する必要があります。
  Stream(40.0, 90.0, 0.0, StreamType(3))
  Stream(150.0, 150.0, 0.0, StreamType(4))

流体の状態
------------

流体の状態 ``state`` は ``enum`` 型である ``StreamState`` を用いて指定します。この値を用\
いて総括伝熱係数の値を指定します。

* ``StreamState.GAS (= 1)``: ガス
* ``StreamState.LIQUID (= 2)``: 液
* ``StreamState.GAS_CONDENSATION (= 3)``: ガス(凝縮)
* ``StreamState.LIQUID_EVAPORATION (= 4)``: 液(蒸発)
* ``StreamState.UNKNOWN (= 5)``: 不明/指定しない。

.. code-block:: python

  # 液体の流体
  Stream(40.0, 90.0, 150.0, state=StreamState(2))

総括伝熱係数の値は、 `プロセスデザインコンテスト <http://scejcontest.chem-eng.kyushu-u.ac.jp/2019/download/processsim2019_v1.pdf>`_
を参考にして以下のように指定しています。

.. _overall_heat_transfer_coefficient:

+--------------------+----------------------+------------------------------------------------------+
| Hot                | Cold                 | U [:math:`\mathrm{W}/\mathrm{m}^2 \cdot \mathrm{K}`] |
+====================+======================+======================================================+
| Gas                | Gas                  | 150                                                  |
+--------------------+----------------------+------------------------------------------------------+
| Liquid             | Gas                  | 200                                                  |
+--------------------+----------------------+------------------------------------------------------+
| Liquid             | Liquid               | 300                                                  |
+--------------------+----------------------+------------------------------------------------------+
| Gas (Condensation) | Liquid (Evaporation) | 1,500                                                |
+--------------------+----------------------+------------------------------------------------------+
| Gas                | Liquid               | 200                                                  |
+--------------------+----------------------+------------------------------------------------------+
| Gas (Condensation) | Gas                  | 500                                                  |
+--------------------+----------------------+------------------------------------------------------+
| Gas (Condensation) | Liquid               | 1,000                                                |
+--------------------+----------------------+------------------------------------------------------+
| Gas                | Liquid (Evaporation) | 500                                                  |
+--------------------+----------------------+------------------------------------------------------+
| Liquid             | Liquid (Evaporation) | 1,000                                                |
+--------------------+----------------------+------------------------------------------------------+

.. note::
  与熱流体には ``StreamState.LIQUID_EVAPORATION`` を、受熱流体には、
  ``StreamState.GAS_CONDENSATION`` を指定することができません。

ID
---

``id_`` は流体を区別するために指定します。複数の流体を作成する場合には、idを重複しないようにす\
る必要があります。
