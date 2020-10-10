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

    def get_indices_subtract(self):
        return abs(self.indices[0] - self.indices[1])


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


def _split_diagonals_by_mid_diagonal(diagonals: List[Diagonal], mid_diagonal: Diagonal) -> Tuple[List[Diagonal], List[Diagonal], List[Diagonal]]:
    left_diagonals = list()
    right_diagonals = list()
    other_diagonals = list()

    min_diagonal_ind = min(mid_diagonal.indices)
    max_diagonal_ind = max(mid_diagonal.indices)

    for diagonal in diagonals:
        if diagonal == mid_diagonal:
            continue

        if diagonal.indices[0] >= min_diagonal_ind and diagonal.indices[1] < max_diagonal_ind:
            left_diagonals.append(diagonal)
        elif diagonal.indices[0] >= max_diagonal_ind and (diagonal.indices[1] > max_diagonal_ind or diagonal.indices[1] <= min_diagonal_ind):
            right_diagonals.append(diagonal)
        else:
            other_diagonals.append(diagonal)

    return left_diagonals, right_diagonals, other_diagonals


def _recalculate_right_diagonals_indices(diagonals_points: List[Tuple[Tuple[int, int], Tuple[int, int]]],
                                         right_polygon_points: List[Tuple[int, int]]) -> List[Diagonal]:
    new_diagonals = list()
    for point1, point2 in diagonals_points:
        new_diagonals.append(Diagonal([right_polygon_points.index(point1), right_polygon_points.index(point2)]))
    return new_diagonals


def _check_triangulation_rec(polygon: Polygon, diagonals: List[Diagonal]) -> bool:
    n = len(polygon.points)
    if n == 3:
        if not diagonals:
            return True
        else:
            return False

    if n != 3 and not diagonals:
        return False

    mid_diagonal = diagonals[0]
    curr_subtract = mid_diagonal.get_indices_subtract()
    for diagonal in diagonals[1:]:
        inds_subtract = diagonal.get_indices_subtract()
        if abs(n - 2 * inds_subtract) < abs(n - 2 * curr_subtract):
            curr_subtract = inds_subtract
            mid_diagonal = diagonal

    # check that mid diagonal is inside the polygon
    p_i = polygon.points[mid_diagonal.indices[0]]
    p_j = polygon.points[mid_diagonal.indices[1]]

    p_i_next = polygon.points[(mid_diagonal.indices[0] + 1) % len(polygon.points)]
    p_i_prev = polygon.points[mid_diagonal.indices[0] - 1]

    v_1 = (p_i_next[0] - p_i[0], p_i_next[1] - p_i[1])
    v_2 = (p_i_prev[0] - p_i[0], p_i_prev[1] - p_i[1])
    v_3 = (p_j[0] - p_i[0], p_j[1] - p_i[1])

    cross_prods = [v_1[0] * v_2[1] - v_1[1] * v_2[0], v_1[0] * v_3[1] - v_1[1] * v_3[0], v_3[0] * v_2[1] - v_3[1] * v_2[0]]
    if not (all(cross_prod >= 0 for cross_prod in cross_prods)
       or (cross_prods[0] < 0) and (not all(cross_prod < 0 for cross_prod in cross_prods[1:]))):
        return False

    left_polygon, right_polygon = _split_polygon_by_mid_diagonal(polygon, mid_diagonal)
    left_diagonals, right_diagonals, other_diagonals = _split_diagonals_by_mid_diagonal(diagonals, mid_diagonal)

    if other_diagonals:
        return False

    # we need to recalculate indices for right diagonals
    right_diagonals_points = list()
    for diagonal in right_diagonals:
        right_diagonals_points.append((polygon.points[diagonal.indices[0]], polygon.points[diagonal.indices[1]]))
    right_diagonals = _recalculate_right_diagonals_indices(right_diagonals_points, right_polygon.points)

    return _check_triangulation_rec(left_polygon, left_diagonals) and _check_triangulation_rec(right_polygon, right_diagonals)


def _run(opts):
    polygon, diagonals = _parse_input_arguments(opts['--input'])
    check_res = _check_triangulation_rec(polygon, diagonals)

    print(f"{str(check_res)}")


if __name__ == "__main__":
    _run(docopt.docopt(__doc__))
