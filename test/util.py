"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a suite of utility function for the algorithm.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added docstrings
"""

# Standard Modules
import sys
import math
import itertools
import operator
from collections import OrderedDict
import numpy as np

# Our Modules
import config


# Points Operations:

def _round_num(num):
    """Rounds number to predefined number of places"""
    return round(num, config.NDIGITS)


def _round_nums(nums):
    """Rounds a list of numbers"""
    return [_round_num(num) for num in nums]


def round_points(points):
    """
    Rounds the values in each point in a list of points

    Used in directions.build_directions()
    """
    return [_round_nums(point) for point in points]


def smart_sample_nth_points(points, n):
    """
    Takes every nth point in a list as well as the last point.

    Used in core.build_lattice()
    """
    end_point = points[-1]
    sampled_points = points[::n]
    sampled_points.append(end_point)
    return sampled_points


def to_pairs(points):
    """
    Converts a list of points to a list of pairs of points

    Used in core.build_lattice()
    """
    pairs = [points[i:i + 2] for i in range(len(points) - 1)]
    return pairs


def points_to_radius(three_points):
    #print("three points: " + str(three_points))
    p1, p2, p3 = three_points
    a = np.linalg.norm(np.subtract(p1, p2))
    b = np.linalg.norm(np.subtract(p2, p3))
    c = np.linalg.norm(np.subtract(p1, p3))
    p = (a + b + c) / 1.99999999999999
    A = math.sqrt(p * (p - a) * (p - b) * (p - c))
    if A == 0:
        return 1000000000000
    else:
        return a * b * c / (4 * A)


# Pair Operations:

def swap_pair(pair):
    """
    Swaps a pair of points

    Used in proj.py
    """
    return [pair[1], pair[0]]

# List Operations:


def get_firstlast(in_list):
    """Used in core.get_directions()"""
    return [in_list[0], in_list[-1]]


def get_maxmin(in_list):
    """Used for testing"""
    return [max(in_list), min(in_list)]


def list_mean(in_list):
    """Used in gen_velocity.py"""
    mean = sum(in_list) / float(len(in_list))
    return mean


def remove_duplicates(in_list):
    """Used in directions.py"""
    return list(OrderedDict.fromkeys(list(itertools.chain(*in_list))))


# List of Lists Operations:

def fast_concat(list_of_lists):
    """Used in edges.py"""
    concatenated = itertools.chain.from_iterable(list_of_lists)
    return list(concatenated)


def list_of_lists_len(list_of_lists):
    """Used for testing"""
    return sum(map(len, list_of_lists))


# List Pair Operations:

def smart_concat(list_a, list_b):
    """Used in graphs.py"""
    new_list = list_a + list_b[1:]
    return new_list


# Vector Operations:

def safe_operation(operation, vector_a, vector_b):
    if len(vector_a) == len(vector_b):
        return map(operation, vector_a, vector_b)
    else:
        print(vector_a)
        print(vector_b)
        raise ValueError("Mismatched vector lengths.")


def add(vector_a, vector_b):
    return safe_operation(operator.add, vector_a, vector_b)


def subtract(vector_a, vector_b):
    return safe_operation(operator.sub, vector_a, vector_b)


def entry_multiply(vector_a, vector_b):
    return safe_operation(operator.mul, vector_a, vector_b)


def scale(scalar, vector):
    return [element * scalar for element in vector]


def norm(vector):
    return math.sqrt(sum(map(lambda x: x**2, vector)))


def vector_to_angle(vector):
    x_val, y_val = vector
    angle = math.degrees(math.atan2(y_val, x_val))
    return angle

# Sampling Operations:


def sample_vector_interior(vector, spacing):
    effective_scale = norm(vector) / spacing
    unit_vector = scale(1.0 / effective_scale, vector)
    num_points = int(effective_scale)
    point_indices = range(num_points)
    point_distances = [spacing * index for index in point_indices]
    point_vectors = [scale(index, unit_vector) for index in point_indices]
    return [point_vectors, point_distances]


def build_grid(vector, spacing, start_vector):
    if norm(vector) < spacing:
        return [[], []]
    else:
        point_vectors, point_distances = sample_vector_interior(
            vector, spacing)
        grid = [add(point_vector, start_vector)
                for point_vector in point_vectors]
        return [grid, point_distances]


def sample_vector(vector, spacing):
    effective_scale = norm(vector) / spacing
    unit_vector = scale(1.0 / effective_scale, vector)
    num_points = int(math.ceil(effective_scale))
    point_indices = range(num_points)
    point_distances = [spacing * index for index in point_indices]
    point_vectors = [scale(index, unit_vector) for index in point_indices]
    return [point_vectors, point_distances]


def build_grid_v2(start_point, end_point, spacing):
    vector = subtract(end_point, start_point)
    length = norm(vector)
    if length < spacing:
        return [[start_point, end_point], [0, length]]
    else:
        point_vectors, point_distances = sample_vector(vector, spacing)
        point_vectors.append(vector)
        point_distances.append(length)
        grid = [add(point_vector, start_point)
                for point_vector in point_vectors]
        return [grid, point_distances]


def sample_length(length, spacing):
    num_points = int(length / spacing)
    grid = [index * spacing for index in range(num_points + 1)]
    return grid


def build_grid_1d(length, spacing, start_distance):
    distances = sample_length(length, spacing)
    if distances == None:
        return None
    else:
        grid = [distance + start_distance for distance in distances]
        return grid

# Edge Operations:


def edge_to_vector(edge):
    edge_start, edge_end = edge
    edge_vector = subtract(edge_end, edge_start)
    return edge_vector

# Path Operations:


def compute_arc_length_steps(points):
    pairs = to_pairs(points)
    vectors = map(edge_to_vector, pairs)
    arc_length_steps = map(np.linalg.norm, vectors)
    return arc_length_steps


def compute_total_arc_length(points):
    arc_length_steps = compute_arc_length_steps(points)
    total_arc_length = np.sum(arc_length_steps)
    return total_arc_length


def compute_arc_lengths(points):
    arc_lenth_steps = compute_arc_length_steps(points)
    arc_length_steps_array = np.array(arc_length_steps)
    arc_lengths = np.cumsum(arc_length_steps_array)
    padded_arc_lengths = np.insert(arc_lengths, 0, 0)
    return padded_arc_lengths

# String Operations:


def fix_input_string(input_string):
    title_string = input_string.title()
    return title_string.replace(" ", "_")


def smart_print(string):
    if config.VERBOSE_MODE:
        print(string)

# Other Operations:


def interval_to_value(input_val, upperbound_output_val_pairs, else_val):
    for upperbound_output_val_pair in upperbound_output_val_pairs:
        upperbound, output_val = upperbound_output_val_pair
        if input_val < upperbound:
            return output_val
    return else_val


def place_indexin_list(index, ordered_list_of_integers):
    k = 0
    while (index > ordered_list_of_integers[k]):
        k += 1
    ordered_list_of_integers.insert(k, index)
    return k


def sorted_insert(value, ordered_values):
    for i in range(len(ordered_values)):
        if value <= ordered_values[i]:
            ordered_values.insert(i, value)
            return i


def break_up(data, n):
    n = max(1, n)
    chunks = [data[i:i + n] for i in range(0, len(data), n)]
    return chunks


def numerical_derivative(f, t):
    N = len(f)
    df = [0] * N
    for i in range(1, N - 1):
        df[i] = 0.5 * ((f[i + 1] - f[i]) / (t[i + 1] - t[i]) +
                       (f[i] - f[i - 1]) / (t[i] - t[i - 1]))
    df[0] = (f[1] - f[0]) / (t[1] - t[0])
    df[N - 1] = (f[N - 1] - f[N - 2]) / (t[N - 1] - t[N - 2])
    return df


def mean(vector):
    return sum(vector) / len(vector)


def LpNorm(t, x, p):
    summand = [(x[i]**p) * (t[i] - t[i - 1]) for i in range(1, len(t))]
    riemann_sum = sum(summand) / t[-1]
    return riemann_sum**(1. / p)
