# pyheatintegration

[![Test](https://github.com/tarao1006/pyheatintegration/actions/workflows/test.yml/badge.svg)](https://github.com/tarao1006/pyheatintegration/actions/workflows/test.yml)

ヒートインテグレーションを支援します。グランドコンポジットカーブ、TQ線図の作成に対応しています。

<details>
  <summary>グランドコンポジットカーブ</summary>
  <img src="./docs/images/grand_composite_curve.png" width="400">
</details>

<details>
  <summary>TQ線図</summary>
  <img src="./docs/images/tq_diagram.png" width="400">
</details>

<details>
  <summary>TQ線図(流体ごとに分割)</summary>
  <img src="./docs/images/tq_diagram_separeted.png" width="400">
</details>

<details>
  <summary>TQ線図(流体ごとに分割。最小接近温度差を満たす。)</summary>
  <img src="./docs/images/tq_diagram_splitted.png" width="400">
</details>

<details>
  <summary>TQ線図(結合可能な熱交換器を結合。)</summary>
  <img src="./docs/images/tq_diagram_merged.png" width="400">
</details>

## Requirements

- Python >= 3.9

## Installation

``` sh
pip install pyheatintegration
```

## Examples

- [simple example](./examples/simple)

## Documentation

https://pyheatintegration.readthedocs.io/en/latest/

## License

MIT
