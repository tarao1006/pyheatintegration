Heat Exchanger Cost
===================

.. note::
  グランドコンポジットカーブやTQ線図の作成方法は :doc:`getting_started` を読んでください。

熱交換器のコストを、以下の式によって推算しています。

.. math::

  \mathrm{Cost [yen]} = 1,500,000 \times A [\mathrm{m^2}]^{0.65} \times k

ここで、 :math:`A` は熱交換器の面積、 :math:`k` は係数で、熱交換器がリボイラーまたは反応器を\
流れる流体に対して用いる場合は ``2.0`` とし、それ以外の場合は ``1.0`` としています。

熱交換器の面積は、以下の式を用いて求めています。

.. math::

  Q = U A \varDelta T_\mathrm{LMTD}

* :math:`Q` [:math:`\mathrm{W}`]: 伝熱量
* :math:`U` [:math:`\mathrm{W}/\mathrm{m}^2 \cdot \mathrm{K}`]: 総括伝熱係数
* :math:`A` [:math:`\mathrm{m^2}`]: 熱交換器面積
* :math:`T_\mathrm{LMTD}` [:math:`\mathrm{K}`]: 対数平均温度差

総括伝熱係数の値は、 `プロセスデザインコンテスト <http://scejcontest.chem-eng.kyushu-u.ac.jp/2019/download/processsim2019_v1.pdf>`_
を参考にして指定しています ( :ref:`総括伝熱係数の表 <overall_heat_transfer_coefficient>` )。\
また、対数平均温度差は向流を仮定して求めています。係数 :math:`k` は ``Stream`` のコンストラ\
クタの引数 ``reboiler_or_reactor`` の値を用いて決定しています。
