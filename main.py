"""
Main file of program.
Lab for checking the triangulation of polygon.

Usage:
    main.py (--input PATH)
    main.py (--help)

Options:
    -i --input PATH     Path to the file, containing input arguments
    -h --help           Show this message
"""

import os
import docopt

from typing import Tuple, List


class Polygon:
    def __init__(self, new_points: List[Tuple[int, int]]):
        self.points = new_points


class Diagonal:
    def __init__(self, new_indices: List[int]):
        self.indices = new_indices
        self.subtract = 2 * abs(self.indices[0] - self.indices[1])


def _parse_input_arguments(file_path: str) -> Tuple[Polygon, List[Diagonal]]:
    if not os.path.exists(file_path):
        raise IOError(f"File '{file_path}' doesn't exist.")

    with open(file_path, "r") as f:
        file_lines = f.read().split('\n')
    num_of_points = int(file_lines[0].strip())
    points = list()
    for line in file_lines[1:num_of_points + 1]:
        coords_strs = line.split(' ')
        points.append((int(coords_strs[0]), int(coords_strs[1])))

    polygon = Polygon(points)

    diagonals = list()
    for line in file_lines[num_of_points + 1:]:
        diagnol_inds_strs = line.split(' ')
        diagonal = Diagonal([int(diagnol_inds_strs[0]), int(diagnol_inds_strs[1])])
        diagonals.append(diagonal)

    return polygon, diagonals


def _split_polygon_by_mid_diagonal(polygon: Polygon, diagonal: Diagonal) -> Tuple[Polygon, Polygon]:
    cur_polygon_points = polygon.points

    min_diagonal_ind = min(diagonal.indices)
    max_diagonal_ind = max(diagonal.indices)

    left_polygon_points = cur_polygon_points[min_diagonal_ind:max_diagonal_ind + 1]
    left_polygon = Polygon(left_polygon_points)

    right_polygon_points = cur_polygon_points[max_diagonal_ind:] + cur_polygon_points[:min_diagonal_ind + 1]
    right_polygon = Polygon(right_polygon_points)

    return left_polygon, right_polygon


def _split_diagonals_by_mid_diagonal(diagonals: List[Diagonal], mid_diagonal: Diagonal, num_of_polygon_points: int) -> Tuple[List[Diagonal], List[Diagonal], bool]:
    left_diagonals = list()
    right_diagonals = list()

    min_diagonal_ind = min(mid_diagonal.indices)
    max_diagonal_ind = max(mid_diagonal.indices)

    for diagonal in diagonals:
        if diagonal == mid_diagonal:
            continue

        cur_min_id = min(diagonal.indices)
        cur_max_id = max(diagonal.indices)

        if max_diagonal_ind >= cur_min_id >= min_diagonal_ind and min_diagonal_ind <= cur_max_id <= max_diagonal_ind:
            left_diagonals.append(Diagonal([cur_min_id - min_diagonal_ind, cur_max_id - min_diagonal_ind]))
        elif (cur_min_id >= max_diagonal_ind or cur_min_id <= min_diagonal_ind) and (cur_max_id >= max_diagonal_ind or cur_max_id <= min_diagonal_ind):
            new_min_id = 0
            new_max_id = 0

            if cur_min_id <= min_diagonal_ind:
                new_min_id = cur_min_id + num_of_polygon_points - max_diagonal_ind
            elif cur_min_id >= max_diagonal_ind:
                new_min_id = cur_min_id - max_diagonal_ind

            if cur_max_id <= min_diagonal_ind:
                new_max_id = cur_max_id + num_of_polygon_points - max_diagonal_ind
            elif cur_max_id >= max_diagonal_ind:
                new_max_id = cur_max_id - max_diagonal_ind

            right_diagonals.append(Diagonal([new_min_id, new_max_id]))
        else:
            return [], [], True

    return left_diagonals, right_diagonals, False


def _check_triangulation_rec(polygon: Polygon, diagonals: List[Diagonal]) -> bool:
    n = len(polygon.points)
    if n == 3:
        if not diagonals:
            return True
        else:
            return False

    if n != 3 and not diagonals:
        return False

    def _key_sort(diagonal: Diagonal):
        return diagonal.subtract

    diagonals.sort(key=_key_sort)

    prev, next = None, None
    for diagonal in diagonals:
        if diagonal.subtract < n:
            prev = diagonal

        if diagonal.subtract >= n:
            next = diagonal
            break

    if not prev:
        mid_diagonal = next
    elif not next:
        mid_diagonal = prev
    else:
        if n - prev.subtract < next.subtract - n:
            mid_diagonal = prev
        else:
            mid_diagonal = next

    # check that mid diagonal is inside the polygon
    p_i = polygon.points[mid_diagonal.indices[0]]
    p_j = polygon.points[mid_diagonal.indices[1]]

    p_i_next = polygon.points[(mid_diagonal.indices[0] + 1) % len(polygon.points)]
    p_i_prev = polygon.points[mid_diagonal.indices[0] - 1]

    v_1 = (p_i_next[0] - p_i[0], p_i_next[1] - p_i[1])
    v_2 = (p_i_prev[0] - p_i[0], p_i_prev[1] - p_i[1])
    v_3 = (p_j[0] - p_i[0], p_j[1] - p_i[1])

    cross_prods = [v_1[0] * v_2[1] - v_1[1] * v_2[0], v_1[0] * v_3[1] - v_1[1] * v_3[0], v_3[0] * v_2[1] - v_3[1] * v_2[0]]
    if not (all(cross_prod > 0 for cross_prod in cross_prods)
       or (cross_prods[0] < 0) and (not all(cross_prod < 0 for cross_prod in cross_prods[1:]))):
        return False

    left_polygon, right_polygon = _split_polygon_by_mid_diagonal(polygon, mid_diagonal)
    left_diagonals, right_diagonals, has_other_diagonals = _split_diagonals_by_mid_diagonal(diagonals, mid_diagonal, len(polygon.points))

    if has_other_diagonals:
        return False

    return _check_triangulation_rec(left_polygon, left_diagonals) and _check_triangulation_rec(right_polygon, right_diagonals)


def _run(opts):
    polygon, diagonals = _parse_input_arguments(opts['--input'])
    check_res = _check_triangulation_rec(polygon, diagonals)

    print(f"{str(check_res)}")


if __name__ == "__main__":
    _run(docopt.docopt(__doc__))
