"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a suite of utility function for the algorithm.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added docstrings
"""

# Standard Modules
import math
import itertools
import operator
from collections import OrderedDict
import numpy as np

# Our Modules
import config

#pylint: disable=C0103, E1101, W0142, W0141

# Points Operations:

def round_num(num):
    """Rounds number to predefined number of places"""
    return round(num, config.NDIGITS)


def round_nums(nums):
    """Rounds a list of numbers"""
    return [round_num(num) for num in nums]


def round_points(points):
    """
    Rounds the values in each point in a list of points

    Used in directions.build_directions()
    """
    return [round_nums(point) for point in points]


def smart_sample_nth_points(points, n_stride):
    """
    Takes every nth point in a list as well as the last point.

    Used in core.build_lattice()
    """
    end_point = points[-1]
    sampled_points = points[::n_stride]
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
    """Convert points to radius
    """
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


def get_list_mean(in_list):
    """Used in gen_velocity.py"""
    list_mean = sum(in_list) / float(len(in_list))
    return list_mean


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
    """Wrapper function for safe vector operations
    """
    if len(vector_a) == len(vector_b):
        return map(operation, vector_a, vector_b)
    else:
        print vector_a
        print vector_b
        raise ValueError("Mismatched vector lengths.")

def add(vector_a, vector_b):
    """Adds a pair of vectors
    """
    return safe_operation(operator.add, vector_a, vector_b)

def subtract(vector_a, vector_b):
    """Subtracts the second vector from the first
    """
    return safe_operation(operator.sub, vector_a, vector_b)

def entry_multiply(vector_a, vector_b):
    """Multiplies a pair of vectors entry by entry
    """
    return safe_operation(operator.mul, vector_a, vector_b)

def scale(scalar, vector):
    """Multiply each element of the vector by the given scale
    """
    return [element * scalar for element in vector]

def norm(vector):
    """Computes the norm of the given vector
    """
    return math.sqrt(sum([x**2 for x in vector]))

def vector_to_angle(vector):
    """Computes the angle of the given vector
    """
    x_val, y_val = vector
    angle = math.degrees(math.atan2(y_val, x_val))
    return angle

# Sampling Operations:

def sample_vector(vector, spacing):
    """Sample points from the interior of a vector at a regular spacing
    """
    effective_scale = norm(vector) / spacing
    unit_vector = scale(1.0 / effective_scale, vector)
    num_points = int(math.ceil(effective_scale))
    point_indices = range(num_points)
    point_distances = [spacing * index for index in point_indices]
    point_vectors = [scale(index, unit_vector) for index in point_indices]
    return [point_vectors, point_distances]


def build_grid(start_point, end_point, spacing):
    """Builds a grid of points between the start and end point.
    """
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
    """sample values within a given length at a regular spacing
    """
    num_points = int(length / spacing)
    values = [index * spacing for index in range(num_points + 1)]
    return values


def build_grid_1d(start_value, end_value, spacing):
    """Build a 1d grid of points in a given interval
    """
    length = end_value - start_value
    values = sample_length(length, spacing)
    if values == None:
        return None
    else:
        grid = [value + start_value for value in values]
        return grid

# Edge Operations:


def edge_to_vector(edge):
    """Convert a given edge to a vector.
    """
    edge_start, edge_end = edge
    edge_vector = subtract(edge_end, edge_start)
    return edge_vector

# Path Operations:


def compute_arc_length_steps(points):
    """Computes the arclength separations between each point in a path of points
    """
    pairs = to_pairs(points)
    vectors = [edge_to_vector(pair) for pair in pairs]
    arc_length_steps = [np.linalg.norm(vector) for vector in vectors]
    return arc_length_steps


def compute_total_arc_length(points):
    """Compute the total arclength of the path defined by the points
    """
    arc_length_steps = compute_arc_length_steps(points)
    total_arc_length = np.sum(arc_length_steps)
    return total_arc_length


def compute_arc_lengths(points):
    """Compute the arclength along the path of each point in the path
    """
    arc_length_steps = compute_arc_length_steps(points)
    arc_length_steps_array = np.array(arc_length_steps)
    arc_lengths = np.cumsum(arc_length_steps_array)
    padded_arc_lengths = np.insert(arc_lengths, 0, 0)
    return padded_arc_lengths

# String Operations:

def fix_input_string(input_string):
    """Convert the input into a string usable for web queries.
    """
    title_string = input_string.title()
    return title_string.replace(" ", "_")

def smart_print(string):
    """Print the input string if verbose mode is turned on.
    """
    if config.VERBOSE_MODE:
        print string

# Other Operations:

def place_indexin_list(index, ordered_list_of_integers):
    """Place index in sorted list of integers while preserving the order
    """
    k = 0
    while index > ordered_list_of_integers[k]:
        k += 1
    ordered_list_of_integers.insert(k, index)
    return k


def sorted_insert(value, ordered_values):
    """Place index in sorted list of integers while preserving the order
    """
    for i in xrange(len(ordered_values)):
        if value <= ordered_values[i]:
            ordered_values.insert(i, value)
            return i

def break_up(data, n):
    """Breaks up a list of data points into chunks n-elements long
    """
    n = max(1, n)
    chunks = [data[i:i + n] for i in range(0, len(data), n)]
    return chunks


def numerical_derivative(f, t):
    """Implements a numerical derivative
    """
    N = len(f)
    df = [0] * N
    for i in range(1, N - 1):
        df[i] = 0.5 * ((f[i + 1] - f[i]) / (t[i + 1] - t[i]) +
                       (f[i] - f[i - 1]) / (t[i] - t[i - 1]))
    df[0] = (f[1] - f[0]) / (t[1] - t[0])
    df[N - 1] = (f[N - 1] - f[N - 2]) / (t[N - 1] - t[N - 2])
    return df


def mean(vector):
    """Computes the mean of a vector
    """
    return sum(vector) / len(vector)

def LpNorm(t, x, p):
    """Computes the discrete L^p norm of a given list of elements
    """
    summand = [(x[i]**p) * (t[i] - t[i - 1]) for i in range(1, len(t))]
    riemann_sum = sum(summand) / t[-1]
    return riemann_sum**(1. / p)
