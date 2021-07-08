from __future__ import annotations

from itertools import chain

Line = tuple[tuple[float, float], tuple[float, float]]


def y_range(lines: list[Line]) -> tuple[float, float]:
    """xy座標系における複数の直線からyの最小値と最大値を返します。

    Args:
        lines list[Line]: 直線。

    Returns:
        tuple[float, float]:
            最小値と最大値。
    """
    return (
        min(line[0][1] for line in lines),
        max(line[1][1] for line in lines)
    )


def extract_x(lines: list[Line]) -> list[float]:
    """xy座標系における複数の直線から重複のないxの値を返します。

    Args:
        lines (list[Line]): 直線。

    Returns:
        list[float]: x座標の値。
    """
    return sorted(list(set(point[0] for point in chain(*lines))))
