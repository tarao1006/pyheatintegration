from __future__ import annotations

from itertools import chain

Line = tuple[tuple[float, float], tuple[float, float]]


def y_range(lines: list[Line]) -> tuple[float, float]:
    """xy座標系における複数の直線からyの最小値と最大値を返します。

    直線は広義単調増加であることを期待しています。

    Args:
        lines list[Line]: 直線。

    Returns:
        tuple[float, float]:
            最小値と最大値。

    Examples:
        >>> y_range([
                ((0, 0), (1, 1)),
                ((1, 1), (2, 2)),
                ((2, 2), (3, 5)),
                ((3, 3), (5, 8))
            ])
        >>> (0, 8)
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

    Examples:
        >>> extract_x([
                ((0, 0), (1, 1)),
                ((1, 1), (2, 2)),
                ((2, 2), (3, 5)),
                ((3, 3), (5, 8))
            ])
        >>> [0, 1, 2, 3, 5]
    """
    return sorted(list(set(point[0] for point in chain(*lines))))
