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
        >>> y_range([((0, 0), (1, 1)), ((1, 1), (2, 2)), ((2, 2), (3, 5)), ((3, 3), (5, 8))])
        (0, 8)
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
        >>> extract_x([((0, 0), (1, 1)), ((1, 1), (2, 2)), ((2, 2), (3, 5)), ((3, 3), (5, 8))])
        [0, 1, 2, 3, 5]
    """
    return sorted(list(set(point[0] for point in chain(*lines))))


def convert_to_excel_data(lines_: list[Line]) -> tuple[list[float], list[float]]:
    """直線のリストをx座標のリストとy座標のリストに変換します。

    Args:
        lines_ (list[Line]): 直線のリスト

    Returns:
        typle[list[float], list[float]]:
            x座標のリストとy座標のリスト

    Examples:
        >>> convert_to_excel_data([((0, 0), (1, 2)), ((1, 2), (3, 3)), ((3, 3), (4, 5))])
        ([0, 1, 3, 4], [0, 2, 3, 5])
        >>> convert_to_excel_data([((0, 0), (1, 2)), ((1, 0), (2, 2))])
        ([0, 1, 1, 2], [0, 2, 0, 2])
    """
    lines = sorted(lines_, key=lambda line: line[0][0])
    x_list = []
    y_list = []

    for i in range(len(lines)):
        x_list.append(lines[i][0][0])
        y_list.append(lines[i][0][1])

        if i != len(lines) - 1 and lines[i][1] == lines[i + 1][0]:
            continue
        x_list.append(lines[i][1][0])
        y_list.append(lines[i][1][1])

    return x_list, y_list
